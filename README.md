# JupyterLite Open World Monitor Prototype

A browser-only JupyterLite prototype for exploring World Monitor's public sandbox without embedding API credentials in GitHub Pages.

## Launch the notebooks

These links point to the GitHub Pages deployment for this repository:

- [00 - Start Here](https://jltobias.github.io/JupyterLite-Open-World-Monitor-Prototype/lab/index.html?path=00_Start_Here.ipynb)
- [01 - Sandbox Catalog](https://jltobias.github.io/JupyterLite-Open-World-Monitor-Prototype/lab/index.html?path=01_Sandbox_Catalog.ipynb)
- [02 - Cross-Domain Monitor](https://jltobias.github.io/JupyterLite-Open-World-Monitor-Prototype/lab/index.html?path=02_Cross_Domain_Monitor.ipynb)

You can also [launch the JupyterLite lab](https://jltobias.github.io/JupyterLite-Open-World-Monitor-Prototype/lab/index.html) and choose a notebook from the file browser.

> The GitHub Pages links become active after the JupyterLite changes are merged into `main` and the Pages deployment workflow completes successfully.

## Data-access model

This prototype uses World Monitor's public deterministic sandbox fixtures. ACLED use is intentionally excluded from the helper layer and notebooks in this repository. For future live production API access, keep World Monitor credentials behind a controlled backend or proxy rather than exposing them in browser-visible notebook code.
