"""World Monitor teaching adapters for CPython and JupyterLite.

Bundled sandbox fixtures are the default. Live calls are explicit and labeled.
This project does not request ACLED operations.
"""
import asyncio
import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DATA = Path(__file__).resolve().parent / "data"
SANDBOX_INDEX = "https://www.worldmonitor.app/sandbox/index.json"
EXCLUDED_OPERATION_IDS = {"ListAcledEvents"}
WORLD_MONITOR_EMBED_URL = (
    "https://www.worldmonitor.app/embed?layers=earthquakes,weather"
    "&center=20,0&zoom=1&theme=dark&variant=full"
)
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"


def display_dashboard(height=600):
    """Show the third-party live embed with an always-visible fallback link."""
    from IPython.display import HTML, display
    height = max(320, min(int(height), 1200))
    return display(HTML(
        f'<p><strong>EXTERNAL LIVE VIEW</strong> · Separate from training data. '
        f'<a href="{WORLD_MONITOR_EMBED_URL}" target="_blank" rel="noopener">Open World Monitor in a new tab</a></p>'
        f'<iframe src="{WORLD_MONITOR_EMBED_URL}" title="World Monitor earthquake and weather embed" '
        f'loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
        f'style="width:100%;height:{height}px;border:1px solid #64748b;border-radius:12px" allowfullscreen></iframe>'
    ))


def panel_dashboard(height=600):
    """Optional compatibility wrapper; install Panel separately to use it."""
    import panel as pn
    pn.extension()
    height = max(320, min(int(height), 1200))
    return pn.Column(pn.pane.Markdown("## External live World Monitor"), pn.pane.HTML(
        f'<iframe src="{WORLD_MONITOR_EMBED_URL}" title="World Monitor live map" '
        f'style="width:100%;height:{height}px;border:0"></iframe>', height=height+20,
        sizing_mode="stretch_width"), sizing_mode="stretch_width")


def fetch_json(url):
    """Compatibility synchronous fetch. Prefer fetch_json_async in new labs."""
    _check_url(url)
    if sys.platform == "emscripten":
        from pyodide.http import open_url
        with open_url(url) as response:
            return json.load(response)
    from urllib.request import urlopen
    with urlopen(url, timeout=15) as response:
        return json.load(response)


def _check_url(url):
    if urlparse(url).scheme != "https":
        raise ValueError("Only HTTPS data endpoints are supported")


async def fetch_json_async(url, timeout=15):
    """CORS-aware browser fetch or a bounded desktop HTTPS request."""
    _check_url(url)
    if sys.platform == "emscripten":
        from pyodide.http import pyfetch
        async def request():
            response = await pyfetch(url)
            if not response.ok:
                raise OSError(f"HTTP {response.status}: {url}")
            return await response.json()
        return await asyncio.wait_for(request(), timeout=timeout)
    return await asyncio.wait_for(asyncio.to_thread(fetch_json, url), timeout=timeout)


def sandbox_index(live=False):
    """Read saved API examples. live=True explicitly refreshes the catalog."""
    index = fetch_json(SANDBOX_INDEX) if live else json.loads((DATA / "worldmonitor/index.json").read_text(encoding="utf-8"))
    index["operations"] = [op for op in index.get("operations", [])
                           if op.get("operationId") not in EXCLUDED_OPERATION_IDS]
    return index


def operations_by_id(live=False):
    return {op["operationId"]: op for op in sandbox_index(live)["operations"]}


def sandbox_fixture(operation_id, live=False):
    if operation_id in EXCLUDED_OPERATION_IDS:
        raise ValueError("This operation is excluded from this teaching repository")
    operations = operations_by_id(live)
    if operation_id not in operations:
        raise KeyError(f"Unavailable operation: {operation_id}; choose {list(operations)}")
    if live:
        return fetch_json(operations[operation_id]["fixture"])
    return json.loads((DATA / "worldmonitor" / f"{operation_id}.json").read_text(encoding="utf-8"))


def response_body(operation_id, live=False):
    return sandbox_fixture(operation_id, live)["response"]["body"]


def validate_geojson(data):
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("Expected a GeoJSON FeatureCollection with a features list")
    return data


async def earthquake_feed(live=False):
    """Return (GeoJSON, provenance). A failed live call is visibly synthetic."""
    stamp = datetime.now(timezone.utc).isoformat()
    reason = None
    if live:
        try:
            data = validate_geojson(await fetch_json_async(USGS_URL))
            return data, dict(mode="LIVE USGS", source=USGS_URL, retrieved_utc=stamp,
                              generated_ms=data.get("metadata", {}).get("generated"), fallback=False)
        except (OSError, ValueError, TimeoutError) as exc:
            reason = f"{type(exc).__name__}: {exc}"
            warnings.warn(f"Live feed unavailable ({reason}); showing SYNTHETIC TRAINING DATA", stacklevel=2)
    data = validate_geojson(json.loads((DATA / "earthquakes_training.geojson").read_text(encoding="utf-8")))
    return data, dict(mode="SYNTHETIC TRAINING" + (" — LIVE FETCH FAILED" if live else ""),
                      source="data/earthquakes_training.geojson", retrieved_utc=stamp,
                      generated_ms=data["metadata"]["generated"], fallback=live, reason=reason)
