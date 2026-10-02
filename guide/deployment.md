# Build, publish and troubleshoot

## Two sites, one publication

JupyterLite stays at the Pages root so existing `/lab/index.html?path=...` URLs continue to work. Jupyter Book is added at `/book/intro.html`. The workflow creates a single Pages artifact containing both. The root redirects visitors to the Book; `/lab/` and `/tree/` remain direct entry points.

This repository uses **Jupyter Book 1.0.4.post1** and its Python/Sphinx toolchain. Jupyter Book 2 is a separate configuration system; upgrading requires an intentional migration from `_config.yml` and `_toc.yml`. See the [version-1 configuration reference](https://jupyter-book.readthedocs.io/v1/customize/config.html).

## Local commands

Use Python 3.11 or later (CI uses 3.11). From the repository root:

```bash
python -m venv .venv
# Windows PowerShell: ./.venv/Scripts/Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/build_site.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000/book/intro.html` and `http://localhost:8000/lab/index.html?path=00_Start_Here.ipynb`. The build executes all notebook cells on the native Python kernel with optional live calls off. Generated files stay in ignored `_build/` and `dist/`. Notebook setup switches to `piplite` only in Pyodide.

CI also runs every code cell in Pyodide 314.0.0, the runtime paired with the pinned Lite kernel. To repeat that compute check with Node 22 or later, run `npm install --prefix _build/wasm --no-audit --no-fund pyodide@314.0.0` and `node scripts/check_pyodide.mjs` after building. This verifies WebAssembly calculations and package installation; it does not replace a browser check of interactive rendering, WebGL, downloads or CORS. The build assigns the Pyodide kernel to published notebook copies while retaining the native kernel in repository sources.

The committed notebook source is generated from `scripts/make_notebooks.py`. To revise its teaching content, edit that script and run it deliberately. `scripts/make_training_data.py` regenerates the fictional fixtures; `scripts/make_visuals.py` regenerates the original graphics. Normal builds do not redownload or regenerate source data.

## GitHub Pages

Enable **Settings → Pages → Build and deployment → Source: GitHub Actions**. A pull request builds and validates without deploying. A push to `main` or a manual workflow on `main` deploys the successful artifact. Inspect Actions for the actual deployment result before calling new links live. No API key or repository secret is needed for the teaching workflow.

When forking, replace `jltobias/JupyterLite-World-Monitor-Prototype` and the corresponding Pages base in the README, notebook-authoring script, intro and configuration. Regenerate notebooks and run the link/build checks. Site assembly uses relative paths, so the artifact works under a repository subpath.

## Common problems

| Symptom | Check / remedy |
|---|---|
| Kernel is starting for a long time | Wait for initial runtime download; check the network allows the configured Pyodide CDN. Try a fresh tab on a supported browser. |
| `ModuleNotFoundError` | Run the first setup cell; keep the helper `.py` files and `data/` alongside notebooks. Restart and run all cells. |
| Notebook appears unchanged after deployment | A browser-saved copy may shadow the new source. Download/rename it before deleting the stale local copy and reopening the published file. |
| Blank interactive map/globe | Check network access to Leaflet/Plotly CDNs, WebGL, and notebook trust. Read the static figure/table alternative. |
| World Monitor iframe blocked | Use its direct link; framing policy is controlled upstream. |
| USGS request fails | Inspect the printed fallback mode and error. CORS, connectivity or provider availability may be involved. Training mode remains usable. |
| Files disappear on another device | Browser storage is per profile/device; use explicit downloads for handover. |
| New notebook URL returns 404 | Confirm the `main` Pages job succeeded and the exact filename matches, including case. |
| Offline map HTML lacks controls | The exported Folium map still uses external JavaScript; use the portable static sitrep HTML for a self-contained briefing. |

## Operating boundaries

This is a static educational publication. It does not supply identity management, shared case storage, reliable background polling, multi-user editing or emergency dispatch. An operational system needs an appropriate backend, governance, security and validation. The notebook architecture demonstrates analysis and communication without claiming to replace those functions.

References: [JupyterLite deployment guide](https://jupyterlite.readthedocs.io/en/stable/howto/deployment/github-pages.html), [JupyterLite standalone serving](https://jupyterlite.readthedocs.io/en/stable/quickstart/standalone.html).
