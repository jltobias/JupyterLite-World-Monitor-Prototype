"""Browser-safe helpers for World Monitor embeds and public sandbox data.

The supported World Monitor embed can be framed by third-party sites. This
repository intentionally requests only the keyless earthquake and weather
layers and excludes the ACLED/conflict operation from sandbox discovery.
"""

import json
from pyodide.http import open_url

SANDBOX_INDEX = "https://www.worldmonitor.app/sandbox/index.json"
EXCLUDED_OPERATION_IDS = {"ListAcledEvents"}
WORLD_MONITOR_EMBED_URL = (
    "https://www.worldmonitor.app/embed"
    "?layers=earthquakes,weather"
    "&center=20,0"
    "&zoom=1"
    "&theme=dark"
    "&variant=full"
)


def display_dashboard(height=680):
    """Display World Monitor's supported live keyless embed in a notebook."""
    from IPython.display import HTML, display

    height = max(320, min(int(height), 1200))
    html = f'''<iframe src="{WORLD_MONITOR_EMBED_URL}" title="World Monitor live map" loading="eager" referrerpolicy="strict-origin-when-cross-origin" style="width:100%;height:{height}px;border:1px solid #444;border-radius:6px;display:block" allowfullscreen></iframe>'''
    return display(HTML(html))


def fetch_json(url):
    """Fetch JSON from a CORS-enabled HTTPS endpoint in JupyterLite/Pyodide."""
    with open_url(url) as response:
        return json.load(response)


def sandbox_index():
    """Return the public sandbox catalog with excluded operations removed."""
    index = fetch_json(SANDBOX_INDEX)
    index["operations"] = [item for item in index.get("operations", []) if item.get("operationId") not in EXCLUDED_OPERATION_IDS]
    return index


def operations_by_id():
    return {item["operationId"]: item for item in sandbox_index()["operations"]}


def sandbox_fixture(operation_id):
    operation = operations_by_id()[operation_id]
    return fetch_json(operation["fixture"])


def response_body(operation_id):
    return sandbox_fixture(operation_id)["response"]["body"]
