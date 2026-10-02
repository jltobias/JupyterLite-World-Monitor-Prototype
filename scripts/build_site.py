"""Build a verified Book + Lite Pages artifact without changing source notebooks."""
import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
os.chdir(ROOT)


def run(*args):
    subprocess.run([sys.executable,*args],check=True)


# Only disposable, resolved build targets under this checkout may be removed.
lite_content = ROOT / "_build/lite-content"
for directory in [DIST, ROOT/"_build/html", lite_content]:
    resolved = directory.resolve()
    if not resolved.is_relative_to(ROOT.resolve()) or resolved == ROOT.resolve():
        raise ValueError(f"Unsafe build output path: {resolved}")
    if directory.exists():
        shutil.rmtree(directory)

# Book executes every core lab and fails on notebook errors and Sphinx warnings.
run("-c","from jupyter_book.cli.main import main; main()","build",".","--all","--warningiserror","--keep-going")
# Native sources use python3; the published Lite copies select its python kernel.
shutil.copytree(ROOT/"content", lite_content,
                ignore=shutil.ignore_patterns("__pycache__", ".ipynb_checkpoints", "exports"))
for notebook in lite_content.glob("*.ipynb"):
    data = json.loads(notebook.read_text(encoding="utf-8"))
    data["metadata"]["kernelspec"] = {"display_name":"Python (Pyodide)","language":"python","name":"python"}
    notebook.write_text(json.dumps(data,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
run("-c","from jupyterlite_core.app import main; main()","build","--contents",str(lite_content),"--output-dir",str(DIST))
shutil.copytree(ROOT/"_build/html",DIST/"book",dirs_exist_ok=True)
(DIST/".nojekyll").touch()
(DIST/"index.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0; url=book/intro.html"><title>World Monitor Field Guide</title>
<h1>World Monitor / JupyterLite Field Guide</h1><p><a href="book/intro.html">Read the Jupyter Book</a></p>
<p><a href="lab/index.html?path=00_Start_Here.ipynb">Run the first JupyterLite lab</a></p></html>''',encoding="utf-8")
run("scripts/check_site.py")
print(f"Ready to serve or deploy: {DIST}")
