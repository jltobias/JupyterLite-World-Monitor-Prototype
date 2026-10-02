"""Meaningful scientific/data-contract and deployment-source checks."""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"content"))
import fieldguide as fg
import worldmonitor as wm


def test_window_denominator_and_unusable_beds():
    s=fg.summarize(days=7)
    districts,reports,facilities=fg.load_tables()
    window=reports[reports.date.between("2025-11-22","2025-11-28")]
    assert s.cases.sum()==window.cases_reported.sum()
    assert np.allclose(s.reported_per_100k,s.cases/s.population*100000)
    assert (s.expected==35).all()
    assert (s.loc[s.functional==0,"usable_beds"]==0).all()
    assert s.attrs==dict(start="2025-11-22",end="2025-11-28",days=7)
    with pytest.raises(ValueError): fg.summarize(days=29)


def test_missing_is_not_zero_and_duplicate_rejected():
    d,r,_=fg.load_tables()
    assert r.loc[r.reports_received==0,"cases_reported"].isna().all()
    with pytest.raises(ValueError,match="Duplicate"):
        fg.validate_reports(pd.concat([r,r.iloc[[0]]]),d)
    bad=r.copy(); bad.loc[bad.reports_received==0,"cases_reported"]=0
    with pytest.raises(ValueError,match="missing"):
        fg.validate_reports(bad,d)
    bad=r.copy(); bad.loc[0,"reports_received"]=6
    with pytest.raises(ValueError,match="received"):
        fg.validate_reports(bad,d)


def test_sandbox_is_local_and_excluded_operations_rejected(monkeypatch):
    def deny(*args,**kwargs): raise AssertionError("Default lab attempted network")
    monkeypatch.setattr(wm,"fetch_json",deny)
    assert len(wm.sandbox_index()["operations"])==4
    assert isinstance(wm.response_body("GetForecasts"),dict)
    with pytest.raises(ValueError): wm.sandbox_fixture("ListAcledEvents")


def test_reference_hashes():
    for item in json.loads((fg.DATA/"provenance.json").read_text()):
        assert hashlib.sha256((fg.DATA/item["path"]).read_bytes()).hexdigest()==item["sha256"]


def test_feed_success_failure_empty_and_malformed(monkeypatch):
    async def failed(url): raise OSError("simulated unavailable feed")
    monkeypatch.setattr(wm,"fetch_json_async",failed)
    with pytest.warns(UserWarning,match="SYNTHETIC"):
        data,meta=asyncio.run(wm.earthquake_feed(live=True))
    assert meta["fallback"] and "FAILED" in meta["mode"]
    assert len(fg.earthquake_table(data))==8
    async def empty(url): return {"type":"FeatureCollection","features":[]}
    monkeypatch.setattr(wm,"fetch_json_async",empty)
    data,meta=asyncio.run(wm.earthquake_feed(live=True))
    assert meta["mode"]=="LIVE USGS" and not meta["fallback"]
    assert fg.earthquake_table(data).empty
    data["features"]=[{"geometry":None}]
    assert fg.earthquake_table(data).attrs["skipped_records"]==1
    with pytest.raises(ValueError): wm.validate_geojson({"error":"blocked"})


def test_sphere_geometry_and_priority_rules():
    x,y,z=fg.xyz(np.array([0,90,180]),np.array([0,0,90]))
    assert np.allclose(x*x+y*y+z*z,1)
    scores=fg.priority_scores(fg.summarize())
    assert scores.exercise_score.between(0,100).all()
    with pytest.raises(ValueError):
        fg.priority_scores(fg.summarize(),{"reported_burden":1,"flood_exposure":1,"access_delay":1})


def test_sitrep_matches_inputs_and_escapes_html():
    s=fg.summarize(); report=fg.sitrep(s)
    assert f"{s.cases.sum():,.0f}" in report
    assert "2025-11-22 to 2025-11-28" in report
    assert "TRAINING EXERCISE" in report and "DRAFT" in report
    link=fg.download_link("safe",'x\" onmouseover=\"evil.html').data
    assert '&quot;' in link


def test_notebook_sources_valid_and_independent():
    import nbformat
    notebooks=list((ROOT/"content").glob("*.ipynb"))
    assert len(notebooks)==12
    for file in notebooks:
        nb=nbformat.read(file,as_version=4); nbformat.validate(nb)
        assert "piplite" in nb.cells[1].source
        assert nb.cells[-1].source.startswith("## Sources")
