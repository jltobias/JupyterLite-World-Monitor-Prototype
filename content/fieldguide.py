"""Small, inspectable teaching utilities. No server, API key or GIS binary needed."""
import base64
import html
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

DATA = Path(__file__).resolve().parent / "data"
TEAL, CORAL, INK = "#007f86", "#db5b45", "#132c46"
TRAINING = "SYNTHETIC EXERCISE · 01–28 Nov 2025 · fictional geography"


def setup_style():
    plt.rcParams.update({"figure.figsize": (10, 5), "figure.dpi": 110, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titleweight": "bold", "axes.labelcolor": INK,
                         "font.size": 11, "axes.prop_cycle": plt.cycler(color=[TEAL, CORAL, "#7662ad", "#c79522"])})


def load_tables():
    districts = pd.read_csv(DATA / "districts.csv")
    reports = pd.read_csv(DATA / "surveillance.csv", parse_dates=["date"])
    facilities = pd.read_csv(DATA / "facilities.csv")
    validate_reports(reports, districts)
    return districts, reports, facilities


def validate_reports(reports, districts):
    """Reject duplicates, bad denominators and impossible reporting counts."""
    if districts["district_id"].duplicated().any() or not (districts.population > 0).all():
        raise ValueError("District identifiers must be unique and populations positive")
    if reports.duplicated(["district_id", "date"]).any():
        raise ValueError("Duplicate district/date reports would double-count cases")
    if reports.date.isna().any() or not set(reports.district_id).issubset(set(districts.district_id)):
        raise ValueError("Unknown district or missing date")
    for col in ("reports_received", "reports_expected"):
        if reports[col].isna().any() or (reports[col] < 0).any() or (reports[col] % 1 != 0).any():
            raise ValueError("Reporting counts must be nonnegative integers")
    if (reports.reports_expected <= 0).any() or (reports.reports_received > reports.reports_expected).any():
        raise ValueError("Reporting counts must satisfy 0 <= received <= expected")
    counts = reports.cases_reported.dropna()
    if (counts < 0).any() or (counts % 1 != 0).any():
        raise ValueError("Case counts must be nonnegative integers or missing")
    if ((reports.reports_received == 0) & reports.cases_reported.notna()).any():
        raise ValueError("No reports is missing, not zero cases")
    if ((reports.reports_received > 0) & reports.cases_reported.isna()).any():
        raise ValueError("Received reports require an observed case count")


def summarize(days=7, end=None):
    """Observed new reports / resident population; never correct for missingness."""
    if not isinstance(days, int) or days <= 0:
        raise ValueError("days must be a positive integer")
    districts, reports, facilities = load_tables()
    end = pd.Timestamp(end) if end is not None else reports.date.max()
    start = end - pd.Timedelta(days=days-1)
    if start < reports.date.min() or end > reports.date.max():
        raise ValueError("Requested window extends beyond the training data")
    window = reports[reports.date.between(start, end)]
    result = window.groupby("district_id").agg(cases=("cases_reported", lambda s: s.sum(min_count=1)),
                                                received=("reports_received", "sum"), expected=("reports_expected", "sum"))
    result = districts.merge(result, on="district_id", validate="one_to_one")
    result["reported_per_100k"] = result.cases / result.population * 100_000
    result["completeness_pct"] = result.received / result.expected * 100
    result = result.merge(facilities[["district_id", "available_beds", "functional", "access_delay_hours"]],
                          on="district_id", validate="one_to_one")
    result["usable_beds"] = result.available_beds * result.functional
    result.attrs.update(start=str(start.date()), end=str(end.date()), days=days)
    return result


def district_geojson():
    return json.loads((DATA / "districts.geojson").read_text(encoding="utf-8"))


def land_rings():
    data = json.loads((DATA / "ne_110m_land.geojson").read_text(encoding="utf-8"))
    for feature in data["features"]:
        geometry = feature["geometry"]
        polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
        for polygon in polygons:
            yield np.asarray(polygon[0])


def district_map(summary, metric="reported_per_100k", title="Reported cases per 100,000 · last 7 days", ax=None):
    """Local polygons avoid network tiles. GeoJSON coordinates are lon, lat."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))
    by_id = summary.set_index("district_id")
    patches, values = [], []
    for f in district_geojson()["features"]:
        patches.append(Polygon(f["geometry"]["coordinates"][0]))
        row = by_id.loc[f["properties"]["district_id"]]
        values.append(row[metric])
    pc = PatchCollection(patches, cmap="YlGnBu", edgecolor="white", linewidth=2)
    pc.set_array(np.array(values, dtype=float))
    ax.add_collection(pc)
    for row in summary.itertuples():
        ax.text(row.longitude, row.latitude, row.district, ha="center", fontsize=9,
                bbox=dict(facecolor="white", alpha=.85, edgecolor="none", pad=2))
    ax.autoscale_view()
    ax.set_aspect(1/np.cos(np.deg2rad(summary.latitude.mean())))
    ax.set(xlabel="Longitude (°)", ylabel="Latitude (°)", title=title)
    ax.figure.colorbar(pc, ax=ax, shrink=.75, label=metric.replace("_", " "))
    ax.text(0, -.2, "Fictional training grid; not administrative boundaries", transform=ax.transAxes, fontsize=9)
    return ax.figure


def leaflet_map(summary):
    import folium
    from branca.colormap import linear
    m = folium.Map(location=[-18.8,35.1], zoom_start=8, tiles=None, control_scale=True)
    lookup = summary.set_index("district_id").to_dict("index")
    cmap = linear.YlGnBu_09.scale(0, max(1, summary.reported_per_100k.max()))
    data = district_geojson()
    for feature in data["features"]:
        row = lookup[feature["properties"]["district_id"]]
        feature["properties"].update(rate=round(row["reported_per_100k"],1), completeness=round(row["completeness_pct"],1))
    folium.GeoJson(data, name="Fictional districts: observed reports", style_function=lambda f: {
        "fillColor": cmap(f["properties"]["rate"]), "color":"#132c46", "weight":1, "fillOpacity":.8},
        tooltip=folium.GeoJsonTooltip(fields=["district","rate","completeness"],
                                     aliases=["Fictional district", "7-day reports / 100,000", "Reports received (%)"])).add_to(m)
    facilities = load_tables()[2]
    group = folium.FeatureGroup(name="Fictional clinics")
    for row in facilities.itertuples():
        folium.Marker([row.latitude,row.longitude], tooltip=f"{row.facility}: {'functional' if row.functional else 'not functional'}",
                      icon=folium.Icon(color="blue" if row.functional else "orange",icon="plus-sign")).add_to(group)
    group.add_to(m)
    folium.TileLayer("OpenStreetMap", name="Optional external OpenStreetMap context", show=False).add_to(m)
    cmap.caption = "SYNTHETIC · reported cases per 100,000 in last 7 days"
    cmap.add_to(m)
    folium.LayerControl().add_to(m)
    m.fit_bounds([[-19.4,34.5],[-18.2,35.7]])
    return m


def xyz(lon, lat, radius=1):
    lon, lat = np.deg2rad(lon), np.deg2rad(lat)
    return radius*np.cos(lat)*np.cos(lon), radius*np.cos(lat)*np.sin(lon), radius*np.sin(lat)


def earthquake_table(data):
    """Drop malformed individual records explicitly; preserve an empty schema."""
    from worldmonitor import validate_geojson
    validate_geojson(data)
    rows, skipped = [], 0
    for feature in data["features"]:
        try:
            if feature["geometry"]["type"] != "Point":
                raise ValueError("Not a point")
            lon,lat,depth = map(float,feature["geometry"]["coordinates"][:3])
            props = feature["properties"]
            mag = float(props["mag"])
            if not np.isfinite([lon,lat,depth,mag]).all() or not (-180<=lon<=180 and -90<=lat<=90):
                raise ValueError("Invalid coordinate or magnitude")
            rows.append(dict(event_id=feature["id"], place=props.get("place","Unknown"), longitude=lon,
                             latitude=lat, depth_km=depth, magnitude=mag))
        except (KeyError, TypeError, ValueError):
            skipped += 1
    result = pd.DataFrame(rows, columns=["event_id","place","longitude","latitude","depth_km","magnitude"])
    result.attrs["skipped_records"] = skipped
    return result


def globe(events, label="SYNTHETIC TRAINING"):
    import plotly.graph_objects as go
    lon,lat = np.meshgrid(np.linspace(-180,180,73),np.linspace(-90,90,37))
    x,y,z = xyz(lon,lat,.99)
    fig = go.Figure(go.Surface(x=x,y=y,z=z,showscale=False,hoverinfo="skip",
                               colorscale=[[0,"#173e59"],[1,"#173e59"]],opacity=1))
    xs,ys,zs = [],[],[]
    for ring in land_rings():
        x,y,z = xyz(ring[:,0],ring[:,1])
        xs.extend([*x,None]); ys.extend([*y,None]); zs.extend([*z,None])
    fig.add_trace(go.Scatter3d(x=xs,y=ys,z=zs,mode="lines",line=dict(color="#59bdb5",width=2),hoverinfo="skip",name="Natural Earth land"))
    x,y,z = xyz(events.longitude.to_numpy(),events.latitude.to_numpy(),1.025)
    fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="markers",text=events.place,
        customdata=events[["magnitude","depth_km"]].to_numpy(),
        hovertemplate="%{text}<br>Magnitude %{customdata[0]}<br>Depth %{customdata[1]} km<extra></extra>",
        marker=dict(size=6,color=events.magnitude,colorscale="YlOrRd",colorbar=dict(title="Magnitude")),name="Events"))
    fig.update_layout(title=f"{label} · drag to rotate the globe",height=580,margin=dict(l=0,r=0,t=55,b=0),
        paper_bgcolor="#081d30",font_color="#e7f2f7",showlegend=False,
        scene=dict(xaxis_visible=False,yaxis_visible=False,zaxis_visible=False,aspectmode="data",bgcolor="#081d30"))
    return fig


def show_plotly(fig):
    """HTML avoids the widget-manager dependency in both Book and Lite."""
    from IPython.display import HTML, display
    display(HTML(fig.to_html(full_html=False,include_plotlyjs="cdn",config={"responsive":True})))


def priority_scores(summary, weights=None):
    """Transparent classroom heuristic, not a validated response/risk model."""
    weights = {"reported_burden":.5,"flood_exposure":.3,"access_delay":.2} if weights is None else weights
    if set(weights) != {"reported_burden","flood_exposure","access_delay"} or any(not np.isfinite(v) or v<0 for v in weights.values()) or not np.isclose(sum(weights.values()),1):
        raise ValueError("Specify three nonnegative finite weights summing to one")
    out = summary.copy()
    out["reported_burden"] = (out.reported_per_100k/300).clip(0,1)
    out["flood_exposure"] = out.flood_pct/100
    out["access_delay"] = (out.access_delay_hours/24).clip(0,1)
    out["exercise_score"] = sum(out[k]*v for k,v in weights.items())*100
    out["review_needed"] = out.completeness_pct < 80
    return out.sort_values("exercise_score",ascending=False)


def download_link(payload, filename, mime="text/plain"):
    """Browser download without exposing a server filesystem path."""
    from IPython.display import HTML
    raw = payload.encode("utf-8") if isinstance(payload,str) else payload
    encoded = base64.b64encode(raw).decode("ascii")
    return HTML(f'<a download="{html.escape(filename,quote=True)}" href="data:{mime};base64,{encoded}">Download {html.escape(filename)}</a>')


def sitrep(summary, operational_period="2025-11-29 08:00–20:00 UTC"):
    """Produce an exercise draft with an explicit data cut-off and action owners."""
    required = {"cases","received","expected","district","reported_per_100k","completeness_pct","usable_beds"}
    if not required.issubset(summary.columns) or not summary.attrs.get("end"):
        raise ValueError("Use summarize() to supply validated data and a reporting window")
    total = summary.cases.sum(min_count=1)
    completeness = 100*summary.received.sum()/summary.expected.sum()
    lead = summary.sort_values("reported_per_100k",ascending=False).iloc[0]
    return f'''# TRAINING EXERCISE — Situation report 001

Status: DRAFT FOR EXERCISE REVIEW. Fictional data; not an operational alert.
Operational period: {operational_period}
Data window: {summary.attrs['start']} to {summary.attrs['end']} inclusive; cut-off 23:59 UTC.
Area: nine fictional training districts. Source: bundled synthetic CSVs, seed 42.

## Current picture
{total:,.0f} reported suspected syndrome cases in this window; reporting completeness {completeness:.1f}%.
{lead.district} has the highest observed reported-case measure ({lead.reported_per_100k:.1f} per 100,000 residents).
There are {summary.usable_beds.sum():.0f} available beds at fictional functional clinics.

## Assessment and uncertainty
Counts represent reports, not confirmed infections. Incomplete reporting can conceal need.
The population is fixed for this exercise; displacement is not modeled. Geographic overlap
with flooding does not establish causation. No patient-level information is included.

## Actions for exercise discussion
| Action | Owner | Due | Completion evidence |
|---|---|---|---|
| Reconcile missing district reports | Surveillance lead | 10:00 UTC | Reporting ledger updated |
| Verify clinic function and access | Operations lead | 12:00 UTC | Dated facility checks |
| Compare resource options with local partners | Planning lead | 14:00 UTC | Decision log and rationale |
| Review and release the next exercise brief | Incident manager | 20:00 UTC | Approved version |

## Information gaps and next update
Unknown: laboratory confirmation, displaced population, road conditions, reporting delays.
Next exercise update: end of operational period. Escalation decisions require authorized review.

## Reproducibility and attribution
Generated by the World Monitor / JupyterLite Field Guide, lab 08.
Data dictionary and provenance: content/data/README.md and content/data/provenance.json.
Context: https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre
Method reading: https://www.cdc.gov/field-epi-manual/php/chapters/describing-epi-data.html
'''


def report_html(markdown, figure):
    buf=io.BytesIO(); figure.savefig(buf,format="png",bbox_inches="tight")
    encoded=base64.b64encode(buf.getvalue()).decode("ascii")
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Training situation report</title><style>body{{max-width:1000px;margin:2rem auto;padding:1rem;font:17px/1.6 system-ui;color:#132c46}}pre{{white-space:pre-wrap;font:inherit}}img{{width:100%}}@media print{{body{{margin:0}}}}</style>
<h1>Exercise briefing · fictional data</h1><img alt="Fictional district reported-case map; values are also supplied in the companion CSV" src="data:image/png;base64,{encoded}">
<pre>{html.escape(markdown)}</pre></html>'''
