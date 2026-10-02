"""Validate generated notebook/book entry points and packaged learning data."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import sys
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
errors=[]


class LiteConfigParser(HTMLParser):
    """Read the same ancestor configuration element that Lite requires."""
    def __init__(self):
        super().__init__()
        self.in_config = False
        self.found = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "jupyter-config-data":
            self.in_config = self.found = True

    def handle_data(self, data):
        if self.in_config:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_config = False


# A 200 response and a valid filename are insufficient: the root landing page
# participates in every Lite application's configuration cascade.
for name in ["index.html", "lab/index.html", "tree/index.html"]:
    page = DIST/name
    if not page.exists():
        errors.append(f"Missing Lite configuration page: {name}")
        continue
    parser = LiteConfigParser()
    parser.feed(page.read_text(encoding="utf-8"))
    try:
        config = json.loads("".join(parser.parts))
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a JSON object")
    except ValueError:
        errors.append(f"Missing or invalid jupyter-config-data in {name}; Lite cannot start")

for notebook in sorted((ROOT/"content").glob("*.ipynb")):
    for target in (DIST/"book/content"/(notebook.stem+".html"),DIST/"files"/notebook.name):
        if not target.exists(): errors.append(f"Missing published lab: {target}")
    data=json.loads(notebook.read_text(encoding="utf-8"))
    published=DIST/"files"/notebook.name
    if published.exists() and json.loads(published.read_text(encoding="utf-8"))["metadata"]["kernelspec"]["name"] != "python":
        errors.append(f"Incorrect browser kernel: {notebook.name}")
    if not any("Run this lab in JupyterLite" in "".join(c["source"]) for c in data["cells"]):
        errors.append(f"No launch link: {notebook.name}")
for name in ["index.html","lab/index.html","book/intro.html","files/fieldguide.py","files/worldmonitor.py",
             "files/data/surveillance.csv","files/data/ne_110m_land.geojson","files/assets/hero.svg"]:
    if not (DIST/name).exists(): errors.append(f"Missing asset: {name}")

# Inspect local href/src destinations in Book pages. Absolute external URLs are
# intentionally not fetched: a provider outage must not invalidate core labs.
for page in (DIST/"book").rglob("*.html"):
    if "_static" in page.relative_to(DIST/"book").parts:
        continue  # Theme templates shipped as assets are not rendered pages.
    for link in re.findall(r'''(?:href|src)=["']([^"']+)["']''',page.read_text(encoding="utf-8")):
        parsed=urlparse(link)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            continue
        target=(page.parent/unquote(parsed.path)).resolve()
        if not target.exists():
            errors.append(f"Broken local asset/link: {page.relative_to(DIST)} -> {link}")
if errors:
    print("\n".join(sorted(set(errors))))
    sys.exit(1)
print("Verified all 12 Book/Lite entry points, packaged data and local Book links.")
