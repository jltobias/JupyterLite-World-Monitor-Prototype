"""Browser-safe helpers for the World Monitor public sandbox.

The public sandbox is deterministic sample data, not live intelligence.
Production API calls require an eligible World Monitor API plan/key and
should not embed secrets in a public JupyterLite/GitHub Pages deployment.
"""

import json
from pyodide.http import open_url

SANDBOX_INDEX = "https://www.worldmonitor.app/sandbox/index.json"


def fetch_json(url):
    """Fetch JSON from a CORS-enabled HTTPS endpoint in JupyterLite/Pyodide."""
    with open_url(url) as response:
        return json.load(response)


def sandbox_index():
    """Return the public World Monitor sandbox operation catalog."""
    return fetch_json(SANDBOX_INDEX)


def operations_by_id():
    """Return sandbox operations keyed by operationId."""
    return {item["operationId"]: item for item in sandbox_index()["operations"]}


def sandbox_fixture(operation_id):
    """Fetch one deterministic sandbox fixture by operationId."""
    operation = operations_by_id()[operation_id]
    return fetch_json(operation["fixture"])


def response_body(operation_id):
    """Return only the sample production response body for an operation."""
    fixture = sandbox_fixture(operation_id)
    return fixture["response"]["body"]
