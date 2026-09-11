# JupyterLite World Monitor Prototype

A browser-only JupyterLite prototype that **displays World Monitor's supported live embed inside the notebooks** and also provides credential-free sandbox examples.

The full World Monitor `/dashboard` page cannot be framed by third-party sites. These notebooks therefore use World Monitor's official `/embed` surface. To honor this repository's no-ACLED requirement, the live embed requests only the **earthquakes** and **weather** layers.

## Live Links

- [Launch 00 - Start Here + Live World Monitor](https://jltobias.github.io/JupyterLite-World-Monitor-Prototype/lab/index.html?path=00_Start_Here.ipynb)
- [Launch 01 - Sandbox Catalog + Live World Monitor](https://jltobias.github.io/JupyterLite-World-Monitor-Prototype/lab/index.html?path=01_Sandbox_Catalog.ipynb)
- [Launch 02 - Cross-Domain Monitor + Live World Monitor](https://jltobias.github.io/JupyterLite-World-Monitor-Prototype/lab/index.html?path=02_Cross_Domain_Monitor.ipynb)
- [Launch JupyterLite Lab](https://jltobias.github.io/JupyterLite-World-Monitor-Prototype/lab/index.html)
- [Open the live World Monitor embed directly](https://www.worldmonitor.app/embed?layers=earthquakes,weather&center=20,0&zoom=1&theme=dark&variant=full)

> The GitHub Pages notebook links become active after the JupyterLite changes are merged into `main` and the Pages deployment workflow completes successfully.

## What the notebooks display

Each notebook includes a code cell that renders this live World Monitor embed as notebook output. Run the first code cell in the notebook to display it:

`https://www.worldmonitor.app/embed?layers=earthquakes,weather&center=20,0&zoom=1&theme=dark&variant=full`

The embed is live World Monitor content. The accompanying API/sandbox cells are separate and use deterministic sample fixtures.

## Data-access model

ACLED use is intentionally excluded from the helper layer and notebooks in this repository. For future live production API access beyond the supported embed, keep World Monitor credentials behind a controlled backend or proxy rather than exposing them in browser-visible notebook code.
