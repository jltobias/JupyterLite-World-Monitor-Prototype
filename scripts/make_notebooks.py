"""Author the learning notebooks. Run deliberately; replaces their cell content.

The generated .ipynb files are committed so GitHub and JupyterLite need no build
step to open them. Keep teaching edits here so regeneration is reproducible.
"""
from pathlib import Path
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://jltobias.github.io/JupyterLite-World-Monitor-Prototype"
BOOT = '''
import sys
if sys.platform == "emscripten":
    import piplite
    await piplite.install(["numpy", "pandas", "matplotlib", "folium==0.20.0", "plotly==6.3.0"])
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from fieldguide import setup_style, load_tables, summarize, TRAINING
setup_style()
print(TRAINING)
'''


def md(text):
    return nbf.v4.new_markdown_cell(textwrap.dedent(text).strip())


def code(text):
    return nbf.v4.new_code_cell(textwrap.dedent(text).strip())


def save(stem, title, intro, cells, references, exercise):
    nb = nbf.v4.new_notebook()
    nb.metadata.update(kernelspec=dict(display_name="Python 3 (ipykernel)",language="python",name="python3"),
                       language_info=dict(name="python"))
    nb.cells = [md(f"# {title}\n\n{intro}\n\n[Run this lab in JupyterLite]({BASE}/lab/index.html?path={stem}.ipynb) · [Book home]({BASE}/book/intro.html)\n\n**Start:** run cells from top to bottom (Shift+Enter), or use Run → Run All Cells. The first launch downloads the Python runtime and packages. Core analysis uses bundled training data; internet is needed for initial setup and interactive JavaScript. Each lab starts independently."),code(BOOT),*cells,
                md("## Practice and debrief\n\n"+textwrap.dedent(exercise).strip()),
                md("## Sources and further learning\n\n"+textwrap.dedent(references).strip())]
    # Stable IDs keep generated diffs reviewable.
    for i,cell in enumerate(nb.cells):
        cell.id=f"{stem[:2]}-cell-{i:02}"
    nbf.validate(nb)
    nbf.write(nb, ROOT / "content" / (stem+".ipynb"))


save("00_Start_Here", "00 · A shared picture, an inspectable analysis",
"**25 minutes · Beginner.** Learn the difference between monitoring, evidence, and a decision. Open a live World Monitor view, run your first analysis, and save your work. No prior GIS experience is required.",[
md('''![Field guide: observe, verify, map, explain, act](assets/hero.svg)

## What World Monitor contributes
World Monitor brings news, map layers and contextual signals into one interface. Its upstream project describes both flat-map and globe views [1]. In this guide, those views start questions; Python notebooks make our transformations and assumptions visible.

| Surface | Job | What a reader can change |
|---|---|---|
| World Monitor | Observe and explore external signals | Layers, map extent and time context |
| Jupyter Book | Explain methods, read outputs and teach | Follow a chapter or download a notebook |
| JupyterLite | Run Python locally in a browser tab | Parameters, charts and a copy of the analysis |
| Reviewed situation report | Communicate a dated assessment | Findings, uncertainty, owners and next update |

## Five-minute World Monitor walkthrough
Open the external view below. Locate a hazard; read its source and timestamp; zoom out for context; compare a second source; write one unanswered question. A blank layer might mean unavailable data. It does not establish that no events occurred.
The embed requests only earthquakes and weather, preserving this repository's exclusion of ACLED. External services can change or refuse embedding; the link also opens directly.'''),
code('''from worldmonitor import display_dashboard, WORLD_MONITOR_EMBED_URL
SHOW_LIVE = False  # Set True to load the external service; not needed for any exercise.
if SHOW_LIVE:
    display_dashboard()
else:
    display(Markdown(f"Live view is off for reproducible reading. [Open World Monitor]({WORLD_MONITOR_EMBED_URL})."))'''),
md('''## Your first inspectable result
Our exercise covers nine **fictional districts**, 28 days, and a suspected syndrome. It is not a report about the real places beneath the demonstration coordinates. Count reports received before interpreting the case counts.'''),
code('''districts, reports, facilities = load_tables()
summary = summarize()
display(summary[["district","population","cases","reported_per_100k","completeness_pct"]].round(1))
print("Reporting window:", summary.attrs)'''),
code('''from fieldguide import district_map
district_map(summary)
plt.show()'''),
md('''## Choose your route
- **EOC briefing:** 00 → 02 → 06 → 07 → 08. Build a common picture and a reviewed draft.
- **Spatial epidemiology:** 00 → 03 → 04 → 05 → 06 → 08. Compare place, time and denominators.
- **Teaching and reuse:** finish 09 → 10 → 11. Publish, facilitate a tabletop and evaluate a handover.

## Save a copy
JupyterLite stores edits in this browser profile; it does not commit them to GitHub or synchronize colleagues' changes. Use File → Save Notebook, then right-click the notebook in the file browser → Download. In lab 08, use explicit report download links. Clearing site data or changing devices can lose local work. Reloaded published notebooks may be shadowed by a saved copy: rename/download that copy before opening a fresh published version.

**Interpretation:** the darkest district needs a closer look at both the numerator and reporting coverage. It is not automatically the district with greatest unmet need.''')],
"[1] [World Monitor project and feature description](https://github.com/koala73/worldmonitor). [2] [JupyterLite documentation](https://jupyterlite.readthedocs.io/en/stable/). [3] [WHO EOC framework](https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre).",
"Change `summarize()` to `summarize(days=14)` and compare the table. Explain why a 14-day numerator must not be compared directly to a 7-day numerator. Deliver one observation, one uncertainty, and one question for a local partner.")

save("01_Sandbox_Catalog", "01 · Sources, schemas and provenance",
"**30 minutes · Beginner.** Inspect real World Monitor API-shaped sandbox examples, distinguish sample from live data, and create a source register.",[
md('''## A catalog is a contract, not an observation
The four bundled fixtures were retrieved from World Monitor's public sandbox on **2 October 2026**. They are upstream deterministic examples, not current conditions. This lab never calls a production endpoint and does not infer public-health risk from a country-risk sample. `data/provenance.json` records the URLs and file hashes.
The saved subset covers country risk, market quotes, chokepoints and forecasts. ACLED is excluded. The optional `live=True` helper refreshes **sandbox examples**, not production data.'''),
code('''from worldmonitor import sandbox_index, sandbox_fixture
index = sandbox_index()
catalog = []
for op in index["operations"]:
    fixture = sandbox_fixture(op["operationId"])
    body = fixture["response"]["body"]
    catalog.append({"operation": op["operationId"], "http_status": fixture["response"]["status"],
                    "body_fields": ", ".join(sorted(body)), "mode":"UPSTREAM SANDBOX SAMPLE"})
display(pd.DataFrame(catalog))'''),
code('''from fieldguide import DATA
import json, hashlib
manifest = json.loads((DATA / "provenance.json").read_text())
checks = [{"asset":x["path"], "matches_recorded_hash":hashlib.sha256((DATA/x["path"]).read_bytes()).hexdigest()==x["sha256"]} for x in manifest]
display(pd.DataFrame(checks))
assert all(x["matches_recorded_hash"] for x in checks)'''),
md('''## Build a source register before combining feeds
A retrieval timestamp answers when we fetched a file. An event timestamp answers when something happened. A publication timestamp answers when a provider released it. Keep all three when available. Freshness alone does not establish correctness. An undocumented denominator or missing time zone can prevent a meaningful join.'''),
code('''register = pd.DataFrame([
    ["World Monitor sandbox", "sample", "fixture-specific", "2026-10-02", "API structure only"],
    ["Fictional surveillance", "synthetic", "2025-11-01 to 28 UTC", "generated, seed 42", "district daily reports"],
    ["USGS optional feed", "live only when requested", "Unix milliseconds UTC", "captured at fetch", "hazard context"],
    ["Natural Earth land", "reference geometry", "not applicable", "v5.1.2", "small-scale geographic context"]
], columns=["source","mode","event_time","version_or_retrieval","appropriate_use"])
display(register)'''),
code('''# A small schema inspection is more useful than dumping the entire payload.
sample = sandbox_fixture("GetChokepointStatus")
print("Envelope:", list(sample))
print("Response fields:", list(sample["response"]))
print("Body fields:", list(sample["response"]["body"]))
fig, ax = plt.subplots(figsize=(9,3))
sizes=[len(sandbox_fixture(op["operationId"])["response"]["body"]) for op in index["operations"]]
ax.barh([op["operationId"] for op in index["operations"]],sizes)
ax.set(xlabel="Number of top-level body fields (schema only)",title="Four saved sandbox contracts")
plt.tight_layout(); plt.show()'''),
md('''**Readout:** the chart compares response structure, not the importance of a topic. Many fields can still describe weak or irrelevant evidence. Preserve a raw copy, document a transformation, and validate the transformed table before mapping it.''')],
"[World Monitor sandbox documentation](https://www.worldmonitor.app/docs/sandbox) · [Public sandbox index](https://www.worldmonitor.app/sandbox/index.json) · [USGS GeoJSON specification](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php).",
"Add a source you would use locally. Record its owner, spatial unit, event and publication time, license, update expectation and known bias. State a question it cannot answer. Do not paste credentials into the notebook.")

save("02_Cross_Domain_Monitor", "02 · Build an EOC common operating picture",
"**35 minutes · Intermediate.** Combine health reporting, exposure and clinic capacity while keeping their meanings separate. Construct a compact briefing panel.",[
md('''## Start with a decision question
**Exercise question:** which districts need verification calls before the next planning meeting? The three panels below show reported burden, reporting completeness, and usable capacity. Their units remain separate. Correlated signals can motivate investigation without establishing a cause.

The original repository's optional Panel wrapper is preserved as `worldmonitor.panel_dashboard()`. This lab uses Matplotlib so every panel also appears in a static book and can be printed. For an optional live layout, install Panel with `await piplite.install("panel")` in Lite, then call the wrapper.'''),
code('''s = summarize()
ordered = s.sort_values("reported_per_100k")
fig, axes = plt.subplots(1,3,figsize=(13,5),sharey=True)
for ax,metric,label,color in zip(axes,["reported_per_100k","completeness_pct","usable_beds"],
    ["Reports per 100,000 · 7 days","Reports received (%)","Usable available beds"],["#007f86","#c79522","#7662ad"]):
    ax.barh(ordered.district,ordered[metric],color=color)
    ax.set_xlabel(label); ax.grid(axis="x",alpha=.2)
axes[1].set_xlim(0,100)
fig.suptitle("SYNTHETIC · Common operating picture · 22–28 Nov 2025")
plt.tight_layout(); plt.show()'''),
md('''## Mark gaps before discussing priorities
Here 80% completeness is a **classroom review trigger**, not a WHO surveillance standard. A flag requests verification. It does not impute the missing cases or rule out urgency in an unflagged district.'''),
code('''review = s.loc[(s.completeness_pct<80) | (s.functional==0),
               ["district","completeness_pct","functional","access_delay_hours"]]
display(review.round(1))
print("Observed cases:", int(s.cases.sum()))
print("Reporting completeness:", round(100*s.received.sum()/s.expected.sum(),1), "%")'''),
code('''from worldmonitor import response_body
# Preserve the cross-domain API exploration: count records, never combine
# country-risk, money and health into an unexplained index.
for operation in ["GetCountryRisk","ListMarketQuotes","GetChokepointStatus","GetForecasts"]:
    body = response_body(operation)
    print(operation, "sample fields:", ", ".join(body))'''),
md('''## Handover structure
![Observe, verify, analyze, brief and review cycle](assets/workflow.svg)
Use a dated snapshot at handover. Link each panel to its source register. Assign a person to resolve each gap and record when the next update is due. Book readers see a reproducible exercise; Lite readers can edit the thresholds and see what changes.''')],
"[WHO EOC framework](https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre) · [World Monitor architecture](https://www.worldmonitor.app/docs/architecture).",
"Create a three-sentence handover: what changed, what is uncertain, and what you need verified by noon. Explain why a country-level sandbox risk score cannot serve as a district disease-incidence estimate.")

save("03_2D_Maps", "03 · Make a map that answers a question",
"**40 minutes · Beginner to intermediate.** Build a choropleth and a layered interactive map, compare counts with population-normalized measures, and inspect reporting gaps.",[
md('''## Counts and denominators answer different questions
Counts help discuss workload. Reported cases per 100,000 residents allow a population-normalized comparison within the same period. Neither measures unobserved infections. We use fixed fictional populations, no displacement adjustment, and the last seven days of reports.

GeoJSON stores **longitude, latitude**. Folium marker positions use **latitude, longitude**. The training grid is located near southeast Africa solely to demonstrate geographic coordinates; it is not a map of actual health districts.'''),
code('''from fieldguide import district_map, leaflet_map
s = summarize()
fig, axes = plt.subplots(1,2,figsize=(13,5))
district_map(s,metric="cases",title="Observed case reports · 7 days",ax=axes[0])
district_map(s,ax=axes[1])
plt.tight_layout(); plt.show()
display(s[["district","cases","population","reported_per_100k","completeness_pct"]].round(1))'''),
md('''## Explore the layers
Hover over a district to see the value and completeness. Toggle clinic markers. The optional OpenStreetMap layer starts off; it is external geographic context, not evidence about our invented districts. Leaflet's JavaScript requires internet access. The static maps above remain available if interactive resources are blocked.'''),
code('''m = leaflet_map(s)
display(m)'''),
code('''from fieldguide import download_link
display(download_link(m.get_root().render(), "training-map.html", "text/html"))'''),
md('''## A second map can reveal why the first is misleading
Missingness should not share a color scale with disease burden. A district with weak reporting may appear reassuringly pale on the case map.'''),
code('''district_map(s,metric="completeness_pct",title="Reports received (%) · same 7-day window")
plt.show()
print("Map limits: rectangles are fictional; colors are relative to this dataset; counts are not confirmation.")''')],
"[Folium getting started](https://python-visualization.github.io/folium/latest/getting_started.html) · [OpenStreetMap attribution](https://www.openstreetmap.org/copyright) · [CDC descriptive epidemiology](https://www.cdc.gov/field-epi-manual/php/chapters/describing-epi-data.html).",
"Choose a district where the workload and normalized rankings differ. Explain the denominator effect. Design a fixed legend for comparing two weeks; independently rescaled colors cannot show change reliably. Export your map and include its training-data label.")

save("04_3D_Globe", "04 · A globe for context, 3D columns for comparison",
"**40 minutes · Intermediate.** Rotate a real geographic globe with fictional hazard points, understand spherical coordinates, and compare a 3D thematic map with a simpler bar chart.",[
md('''## 3D is a choice of representation
A globe helps with planetary context and the date line. It also hides the far hemisphere. The map below uses bundled Natural Earth land outlines on a unit sphere; no map API key or imagery tiles are needed. Its points are **invented earthquake-format events**. The globe is not a terrain model, and point height does not encode earthquake depth.
Plotly JavaScript loads from its CDN and requires WebGL. If unavailable, use the 2D companion immediately below.'''),
code('''from worldmonitor import earthquake_feed
from fieldguide import earthquake_table, globe, show_plotly, land_rings
data, provenance = await earthquake_feed(live=False)
events = earthquake_table(data)
print(provenance["mode"])
show_plotly(globe(events,provenance["mode"]))'''),
code('''fig, ax = plt.subplots(figsize=(12,5))
for ring in land_rings():
    ax.fill(ring[:,0],ring[:,1],color="#dce6eb",edgecolor="#829aa8",linewidth=.3)
scatter=ax.scatter(events.longitude,events.latitude,c=events.magnitude,cmap="YlOrRd",s=65,edgecolor="#132c46")
fig.colorbar(scatter,ax=ax,label="Magnitude (synthetic)")
ax.set(xlim=(-180,180),ylim=(-60,85),xlabel="Longitude (°)",ylabel="Latitude (°)",title="SYNTHETIC events · 2D companion · Natural Earth land")
plt.show()
display(events)'''),
md('''## Build the sphere yourself
For longitude λ and latitude φ in radians: `x=cos(φ)cos(λ)`, `y=cos(φ)sin(λ)`, `z=sin(φ)`. A unit-radius check catches coordinate errors. Longitude spacing on a flat equirectangular map does not represent equal ground distances at all latitudes.'''),
code('''from fieldguide import xyz
x,y,z=xyz(events.longitude.to_numpy(),events.latitude.to_numpy())
assert np.allclose(x*x+y*y+z*z,1)
print("Every point lies on the unit sphere.")'''),
md('''## Extrude a district measure, not terrain
The height below is reported cases per 100,000 for seven days. The horizontal axes are longitude and latitude; the vertical axis is a health-reporting measure, **not meters**. Occlusion and perspective complicate comparison, so a sorted bar chart accompanies the 3D map.'''),
code('''s=summarize()
fig=plt.figure(figsize=(13,5))
ax=fig.add_subplot(121,projection="3d")
ax.bar3d(s.longitude-.13,s.latitude-.13,np.zeros(len(s)),.26,.26,s.reported_per_100k,color="#007f86",shade=True)
ax.set(xlabel="Longitude (°)",ylabel="Latitude (°)",zlabel="Reports / 100,000",title="SYNTHETIC thematic columns")
ax.view_init(elev=28,azim=-55)
ax2=fig.add_subplot(122)
ordered=s.sort_values("reported_per_100k")
ax2.barh(ordered.district,ordered.reported_per_100k)
ax2.set(xlabel="Reports per 100,000 · 7 days",title="Same values, easier comparison")
plt.tight_layout(); plt.show()''')],
"[Natural Earth public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/) · [Plotly 3D scatter](https://plotly.com/python/3d-scatter-plots/) · [World Monitor dual map engines](https://github.com/koala73/worldmonitor).",
"Rotate the globe until an event disappears behind it. Explain how a screenshot could omit evidence. Change the 3D column camera angle and identify whether the top district remains obvious. Choose the better display for a printed sitrep and justify it.")

save("05_Spatial_Epidemiology", "05 · Time, place and the denominator",
"**45 minutes · Intermediate.** Draw a report-date curve, compare district measures, and explore population sensitivity without claiming causal effects.",[
md('''## Define the numerator before drawing a curve
Our fictional definition is **new suspected-syndrome case reports received by a district on a calendar day**. It is not a laboratory-confirmed case definition. We have report dates, not onset dates, so this is a **report-date curve**, not an onset-based epidemic curve. Real work would specify symptoms, eligibility, geography, onset and deduplication rules.
Read CDC's descriptive-epidemiology chapter for the distinction between counts, time and population comparisons [1]. The calculations here are an original teaching example.'''),
code('''districts,reports,facilities=load_tables()
daily=reports.groupby("date").agg(cases=("cases_reported",lambda x:x.sum(min_count=1)),received=("reports_received","sum"),expected=("reports_expected","sum"))
fig,axes=plt.subplots(2,1,figsize=(11,6),sharex=True)
axes[0].bar(daily.index,daily.cases,width=1,color="#007f86")
axes[0].set(ylabel="New reported cases",title="SYNTHETIC · Report-date curve, not symptom onset")
axes[1].plot(daily.index,100*daily.received/daily.expected,marker="o",color="#db5b45")
axes[1].set(ylabel="Completeness (%)",ylim=(0,105),xlabel="Report date, November 2025 (UTC)")
fig.autofmt_xdate(); plt.tight_layout(); plt.show()'''),
md('''## Work the formula in the notebook
Seven-day observed reports per 100,000 = `sum(new reported cases in window) / resident population × 100,000`.
The label matters: it is an observed reporting measure. We do not divide by completeness to pretend we recovered unobserved cases. Districts can differ in access, care-seeking, definitions, testing and reporting delay.'''),
code('''window=reports[reports.date.between("2025-11-22","2025-11-28")]
counts=window.groupby("district_id").cases_reported.sum(min_count=1)
analysis=districts.merge(counts.rename("cases"),on="district_id",validate="one_to_one")
analysis["reported_per_100k"]=analysis.cases/analysis.population*100000
display(analysis[["district","cases","population","reported_per_100k"]].round(1))
assert np.allclose(analysis.reported_per_100k,summarize().reported_per_100k)'''),
md('''## Sensitivity is not a confidence interval
Suppose the actual population were 20% lower or higher than our fixed estimate. Show the resulting range. These are **chosen scenario bounds**, not statistical confidence limits. They do not capture under-reporting or diagnostic uncertainty.'''),
code('''a=analysis.sort_values("reported_per_100k").copy()
low=a.cases/(a.population*1.2)*100000
high=a.cases/(a.population*.8)*100000
fig,ax=plt.subplots(figsize=(10,5))
ax.errorbar(a.reported_per_100k,a.district,xerr=[a.reported_per_100k-low,high-a.reported_per_100k],fmt="o",capsize=4)
ax.set(xlabel="Observed reports per 100,000 · 7 days",title="SYNTHETIC · ±20% population scenario (not a confidence interval)")
plt.show()'''),
code('''s=summarize()
fig,ax=plt.subplots()
points=ax.scatter(s.flood_pct,s.reported_per_100k,c=s.completeness_pct,cmap="viridis",s=85)
for row in s.itertuples():
    ax.annotate(row.district,(row.flood_pct,row.reported_per_100k),xytext=(4,4),textcoords="offset points",fontsize=8)
fig.colorbar(points,ax=ax,label="Reporting completeness (%)")
ax.set(xlabel="Fictional population exposed to flood (%)",ylabel="Reports per 100,000 · 7 days",title="An ecological pattern to investigate, not a causal estimate")
plt.show()'''),
md('''**Readout:** these associations were partly built into the synthetic generator. They are not evidence of a real exposure–disease relationship. Area-level associations also cannot establish an individual's exposure or risk (the ecological inference problem). Different boundary groupings can change apparent patterns.''')],
"[1] [CDC: Describing epidemiologic data](https://www.cdc.gov/field-epi-manual/php/chapters/describing-epi-data.html). [2] [CDC: Designing analytic studies](https://www.cdc.gov/field-epi-manual/php/chapters/design-conduct-analyze-field-studies.html).",
"Identify two explanations for a falling report-date curve other than falling illness. Propose the additional fields needed for an onset curve. Explain why the denominator sensitivity bars cannot be called 95% confidence intervals.")

save("06_Data_Quality", "06 · Missing data is part of the picture",
"**35 minutes · Intermediate.** Validate inputs, map reporting coverage across time, and prevent silence from being encoded as zero.",[
md('''## Four checks before a briefing
Require unique district/date keys, positive denominators, known district identifiers, and nonnegative reporting counts with received ≤ expected. Missing counts when no report was received must remain missing.
This exercise assumes **five reports expected per district per day**. A complete system would retain facility-level reporting records and distinguish late, revised, duplicate and zero-case reports.'''),
code('''from fieldguide import validate_reports
districts,reports,facilities=load_tables()
validate_reports(reports,districts)
display(reports.loc[reports.cases_reported.isna()])
print("Validated rows:",len(reports))'''),
code('''quality=reports.assign(completeness=100*reports.reports_received/reports.reports_expected)
matrix=quality.pivot(index="district_id",columns="date",values="completeness")
fig,ax=plt.subplots(figsize=(12,4))
im=ax.imshow(matrix,vmin=0,vmax=100,cmap="cividis",aspect="auto")
ax.set_yticks(range(len(matrix)),districts.set_index("district_id").loc[matrix.index,"district"])
ax.set_xticks(range(0,28,3),[d.strftime("%d %b") for d in matrix.columns[::3]])
ax.set(title="SYNTHETIC · Reporting completeness by district and day",xlabel="Report date (2025)")
fig.colorbar(im,ax=ax,label="Reports received (%)")
plt.tight_layout(); plt.show()'''),
md('''## Show the failure, then explain it
A duplicated row would double-count part of the numerator. Catch the problem before aggregation. The original table is preserved for the rest of the lab.'''),
code('''bad=pd.concat([reports,reports.iloc[[0]]],ignore_index=True)
try:
    validate_reports(bad,districts)
except ValueError as error:
    print("Correctly rejected:",error)
missing=pd.Series([np.nan,np.nan])
print("Default sum (misleading for all-missing):",missing.sum())
print("sum(min_count=1), preserving unknown:",missing.sum(min_count=1))'''),
md('''## Completeness is a review signal
Separate quality flags from response priorities. Poor reporting can coincide with disrupted infrastructure and greater need. Do not automatically lower a district's priority simply because its data are incomplete.'''),
code('''s=summarize()
s["needs_reporting_review"]=s.completeness_pct<80
display(s[["district","completeness_pct","cases","needs_reporting_review"]].round(1))
print("80% is a teaching threshold; select and justify local rules with responsible data owners.")''')],
"[CDC field investigation methods](https://www.cdc.gov/field-epi-manual/php/chapters/field-investigation.html) · [pandas sum and min_count](https://pandas.pydata.org/docs/reference/api/pandas.Series.sum.html).",
"Change the classroom completeness trigger from 80% to 90%. Identify the newly flagged districts and the verification workload created. Describe how you would handle a revised report without counting both versions.")

save("07_EOC_Planning", "07 · Compare priorities and expose assumptions",
"**45 minutes · Intermediate.** Build a transparent exercise score, test weight sensitivity, and create a decision log with owners and verification steps.",[
md('''## A score supports discussion; it does not authorize action
We combine three fictional signals with explicit weights: reported burden (50%), flood exposure (30%) and access delay (20%). Fixed classroom anchors are 300 reports per 100,000, 100% exposed population and 24 hours of delay. Each component is clipped to 0–1, then the weighted sum is multiplied by 100.
These anchors and weights are **not calibrated, validated, or recommended operational thresholds**. The algorithm excludes information quality from the score and displays it separately. A real planning meeting also needs local knowledge, feasibility, equity, existing commitments and responsible authority.'''),
code('''from fieldguide import priority_scores
s=summarize()
ranked=priority_scores(s)
display(ranked[["district","exercise_score","completeness_pct","review_needed","usable_beds"]].round(1))'''),
code('''fig,ax=plt.subplots(figsize=(10,5))
left=np.zeros(len(ranked))
for component,weight in {"reported_burden":.5,"flood_exposure":.3,"access_delay":.2}.items():
    width=ranked[component].to_numpy()*weight*100
    ax.barh(ranked.district,width,left=left,label=component.replace("_"," "))
    left+=width
ax.invert_yaxis(); ax.set(xlabel="Exercise score (0–100)",title="SYNTHETIC · Contributions to a discussion score")
ax.legend(loc="lower right"); plt.show()'''),
md('''## Test sensitivity before defending a rank
Reweighting access changes the question being answered. Display both rankings. A stable rank under these two choices is not proof of a valid model.'''),
code('''alternative=priority_scores(s,{"reported_burden":.2,"flood_exposure":.3,"access_delay":.5})
rank_a=ranked.reset_index(drop=True).assign(baseline_rank=lambda x:x.index+1)
rank_b=alternative.reset_index(drop=True).assign(access_rank=lambda x:x.index+1)
comparison=rank_a[["district","baseline_rank"]].merge(rank_b[["district","access_rank"]],on="district")
display(comparison)
fig,ax=plt.subplots(figsize=(9,5))
for r in comparison.itertuples():
    ax.plot([0,1],[r.baseline_rank,r.access_rank],"o-",alpha=.6)
    ax.text(-.03,r.baseline_rank,r.district,ha="right",fontsize=9)
ax.set_xticks([0,1],["Baseline weights","More weight on access"])
ax.set(ylabel="Rank (1 first)",title="SYNTHETIC · Sensitivity of discussion order",xlim=(-.5,1.2))
ax.invert_yaxis(); plt.show()'''),
code('''log=pd.DataFrame([
    {"district":r.district,"proposed_step":"Verify need and access with district focal point",
     "owner":"Planning lead","due_utc":"2025-11-29 12:00","status":"EXERCISE — pending verification",
     "reason":f"Discussion score {r.exercise_score:.1f}; completeness {r.completeness_pct:.1f}%"}
    for r in ranked.head(3).itertuples()])
display(log)
from fieldguide import download_link
display(download_link(log.to_csv(index=False),"exercise-decision-log.csv","text/csv"))''')],
"[WHO public health EOC framework](https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre) · [WHO emergency operations](https://www.who.int/emergencies/operations).",
"Write an alternative prioritization rule without a composite score. Compare its top three districts with the weighted result. State an equity concern and what information could change your recommendation. Record the owner, review time and evidence needed in the decision log.")

save("08_Situation_Reports", "08 · Publish a reproducible situation report",
"**40 minutes · Intermediate.** Convert the same validated inputs into an exercise sitrep, a map, a CSV and a portable briefing bundle.",[
md('''## A useful sitrep is a dated, reviewable claim
Include the operational period, data cut-off, geographic scope, current picture, uncertainty, actions with owners, information gaps and next update. Keep what was observed separate from interpretation and proposed action. This is an original educational template informed by EOC practice; it is not an official WHO or agency form.
The generated briefing is labeled **TRAINING EXERCISE** and **DRAFT**. Use the download links to move files out of browser storage. Nothing is emailed or uploaded.'''),
code('''from fieldguide import sitrep, district_map, report_html, download_link
s=summarize()
brief=sitrep(s)
display(Markdown(brief))'''),
code('''fig=district_map(s)
plt.show()
portable_html=report_html(brief,fig)
display(download_link(brief,"training-sitrep.md","text/markdown"))
display(download_link(portable_html,"training-sitrep.html","text/html"))
display(download_link(s.to_csv(index=False),"training-indicators.csv","text/csv"))'''),
md('''## Package evidence with the narrative
The ZIP contains a self-contained HTML brief with an embedded image, Markdown, a numeric CSV, a source manifest and a map PNG. It opens without an interactive map server. A generated-at timestamp is distinct from the exercise data cut-off.'''),
code('''import io,json,zipfile,hashlib
from datetime import datetime,timezone
from fieldguide import DATA
image_bytes=io.BytesIO()
fig.savefig(image_bytes,format="png",bbox_inches="tight")
metadata={"mode":"SYNTHETIC TRAINING", "generated_utc":datetime.now(timezone.utc).isoformat(),
          "data_window":s.attrs,"generator_seed":42,
          "input_sha256":{name:hashlib.sha256((DATA/name).read_bytes()).hexdigest()
                          for name in ["districts.csv","surveillance.csv","facilities.csv"]}}
bundle=io.BytesIO()
with zipfile.ZipFile(bundle,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("training-sitrep.md",brief)
    z.writestr("training-sitrep.html",portable_html)
    z.writestr("training-indicators.csv",s.to_csv(index=False))
    z.writestr("training-map.png",image_bytes.getvalue())
    z.writestr("manifest.json",json.dumps(metadata,indent=2))
display(download_link(bundle.getvalue(),"training-briefing.zip","application/zip"))
print("Bundle size:",round(len(bundle.getvalue())/1024),"KiB")'''),
code('''# Cross-check the brief against its source table before reviewing the prose.
assert f"{s.cases.sum():,.0f}" in brief
assert s.attrs["end"] in brief
assert "TRAINING EXERCISE" in brief and "DRAFT" in brief
assert set(zipfile.ZipFile(io.BytesIO(bundle.getvalue())).namelist()) == {
    "training-sitrep.md","training-sitrep.html","training-indicators.csv","training-map.png","manifest.json"}
print("Numeric, date, exercise-label and bundle checks passed.")'''),
md('''## Review with a partner
Can another person reproduce the numerator and date window from the CSV? Is every map labeled? Are gaps visible? Does every proposed action have an owner and time? Read the HTML with a screen reader or without the image: the written brief and CSV should carry the key facts. Printing the HTML to PDF is available through your browser.''')],
"[WHO EOC framework](https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre) · [JupyterLite file persistence](https://jupyterlite.readthedocs.io/en/stable/).",
"Prepare a five-line executive brief from the output, keeping the training label. Add a local-language summary and a revision number. Exchange ZIP files with a classmate and ask them to find the data cut-off, denominator, main gap and next action without opening Python.")

save("09_Live_Data", "09 · Connect a public feed without hiding failures",
"**35 minutes · Intermediate.** Fetch an optional public USGS feed, retain provenance, handle failures visibly and distinguish live content from saved training examples.",[
md('''## Browser constraints are part of the architecture
Browser Python uses HTTP endpoints permitted by CORS; it cannot bypass provider policy. Secret API keys do not belong in a public notebook. Use a controlled backend for authenticated production services. This optional example uses the public USGS M4.5+ past-week GeoJSON feed and requires no credential.
Default mode is synthetic. Set `USE_LIVE=True` explicitly to make a request. A failed request warns and returns data labeled **SYNTHETIC TRAINING — LIVE FETCH FAILED**. It never silently presents a fixture as live.'''),
code('''from worldmonitor import earthquake_feed
from fieldguide import earthquake_table
USE_LIVE=False
feed,provenance=await earthquake_feed(live=USE_LIVE)
display(pd.Series(provenance,name="Provenance"))
events=earthquake_table(feed)
print("Valid rows:",len(events),"Skipped malformed rows:",events.attrs["skipped_records"])
display(events)'''),
md('''## Retain event time and source-generation time
USGS provides time in Unix milliseconds and coordinates in longitude, latitude, depth order. Depth is in kilometers. Magnitude is not impact: exposure, vulnerability, distance and local conditions matter. An empty valid feed should produce zero rows, not a fabricated event.'''),
code('''generated=provenance.get("generated_ms")
if generated is not None:
    print("Feed generated (UTC):",pd.to_datetime(generated,unit="ms",utc=True))
event_times=[f.get("properties",{}).get("time") for f in feed["features"]]
times=pd.to_datetime(pd.Series(event_times,dtype="float64"),unit="ms",utc=True,errors="coerce")
print("Earliest event time:",times.min(),"Latest:",times.max())
fig,ax=plt.subplots(figsize=(10,4))
if len(events):
    ax.hist(events.magnitude,bins=8,color="#007f86",edgecolor="white")
else:
    ax.text(.5,.5,"No valid events in this response",ha="center",transform=ax.transAxes)
ax.set(xlabel="Magnitude",ylabel="Event count",title=provenance["mode"]+" · Earthquake feed")
plt.show()'''),
code('''from fieldguide import download_link
import json
export={"provenance":provenance,"geojson":feed}
display(download_link(json.dumps(export,indent=2),"hazard-feed-with-provenance.json","application/json"))'''),
md('''## Production extension pattern
`Browser notebook → authorized backend → provider API`.
The backend holds secrets and implements quotas, caching, access controls and allowed origins. Publish only an appropriately aggregated, licensed response. JupyterLite is not a shared database or an incident-management authority. Record schema changes and freshness checks, and retain a reproducible snapshot alongside a briefing.''')],
"[USGS GeoJSON feed specification](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) · [Pyodide HTTP API](https://pyodide.org/en/stable/usage/api/python-api/http.html) · [World Monitor sandbox](https://www.worldmonitor.app/docs/sandbox).",
"Run once in synthetic mode, then optionally in live mode. Compare provenance, not just event counts. Explain the difference between event time, feed-generation time and retrieval time. Never join this global hazard feed to fictional clinic data as if it represented observed impacts.")

save("10_Teaching_and_Sharing", "10 · Teach, adapt and share the field guide",
"**30 minutes · All levels.** Plan a short workshop, learn what a static deployment shares, and adapt the materials for bandwidth, language and accessibility.",[
md('''## Democratization is a design task
A public Book lowers the cost of reading a method. Lite lowers the installation barrier to running it. Both still require a capable browser, initial downloads and access to the published assets. Offline-friendly tables and static maps help people who cannot load a globe. A downloadable brief reaches people who will not run Python.

![Learning and briefing workflow](assets/workflow.svg)

## A 90-minute workshop
| Time | Activity | Evidence of learning |
|---|---|---|
| 0–15 min | Observe a World Monitor layer; inspect source and time | One verifiable question |
| 15–35 min | Run labs 03 and 06 | Map plus a completeness statement |
| 35–55 min | Compare denominators and priorities | One changed assumption and its effect |
| 55–80 min | Generate lab 08's briefing | Downloaded exercise ZIP |
| 80–90 min | Peer handover | Recipient can identify the next action |

## Video learning with an accessible alternative
1. [WHO EIOS Global Technical Meeting 2021: day 3, track 2, webinar 3](https://www.who.int/initiatives/eios/global-technical-meeting-2021/day3/webinar-3) includes an official video and session context. Watch for how an external signal becomes a verification task; record one example. Use the page's session description if video is blocked.
2. [WHO Science in 5, episode 124: mpox](https://www.who.int/podcasts/episode/science-in-5/episode--124---mpox--what-you-need-to-know) includes video and a transcript. This **historical communication example is not current clinical guidance**. Compare its explanation of uncertainty with your exercise briefing.
3. The [original animated training timeline](assets/reporting-timeline.gif) is generated from the same synthetic CSV. Its text equivalent: counts rise during the exercise while later reporting completeness falls; observed counts alone cannot establish the underlying trend.

External videos remain on their publishers' sites; this project does not redistribute them or imply their endorsement.'''),
code('''# List the shareable artifacts and their different roles.
artifacts=pd.DataFrame([
    ["Book HTML","Read methods and rendered results","Public static files"],
    ["Notebook (.ipynb)","Inspect and change calculations","Download a copy"],
    ["Briefing ZIP","Read and audit a dated exercise summary","Portable, no kernel"],
    ["CSV + dictionary","Recompute indicators in another tool","Explicit units and missingness"]
],columns=["artifact","reader_task","sharing_model"])
display(artifacts)'''),
md('''## Fork and publish
The repository's GitHub Actions workflow builds the Book into `/book/` and JupyterLite into the site root, keeping old `/lab/` links valid. Enable **Settings → Pages → Source: GitHub Actions**. Update the repository URL and launch base in `scripts/make_notebooks.py`, `README.md`, `intro.md`, `_config.yml` and the guide if you fork. Regenerate notebooks and verify all links before publishing.

For local builds, follow the README. This project intentionally pins the Python-based **Jupyter Book 1** toolchain; Jupyter Book 2 uses a different MyST configuration and must not be substituted without migration.

## Reuse with care
Translate narrative, labels and the source register together. Keep original units visible. Use text and symbols as well as color; give maps a table alternative. Remove patient identifiers and small-area identifying details before preparing public teaching data. Public Pages and browser storage are not a clinical records platform.'''),
code('''# A print-friendly accessibility check for the exercise table.
s=summarize()
table=s[["district","population","cases","reported_per_100k","completeness_pct"]].round(1)
print(table.to_string(index=False))''')],
"[JupyterLite GitHub Pages guide](https://jupyterlite.readthedocs.io/en/stable/howto/deployment/github-pages.html) · [Jupyter Book 1 configuration](https://jupyter-book.readthedocs.io/v1/customize/config.html) · [WHO EIOS video session](https://www.who.int/initiatives/eios/global-technical-meeting-2021/day3/webinar-3).",
"Prepare a workshop for a participant who has only a phone and intermittent internet. Specify which exported artifacts they receive, an accessible text alternative, and how they can contribute to the interpretation without running a notebook.")

save("11_Capstone", "11 · Tabletop: the next operational period",
"**60–90 minutes · Capstone.** Act as a small EOC analysis cell supporting spatial epidemiologists. Deliver a verified exercise briefing and explain the limits of your recommendation.",[
md('''## Scenario
It is **29 November 2025, 08:00 UTC in the fictional exercise**. A coastal flood has disrupted clinic access. Suspected-syndrome reports increased, but several districts now submit fewer reports. The incident manager needs a briefing for the next operational period. Every district, facility and health value is invented.

Assign four roles: surveillance analyst, mapping analyst, planning liaison and reviewer. One person may fill multiple roles. Work from the same cut-off and keep a decision log.

## Required products
1. A source register separating external context from synthetic analysis.
2. A 2D map and a table using the same period and denominator.
3. A report-date curve with reporting completeness alongside it.
4. A justified use of the 3D globe, or a reason to omit it from the briefing.
5. Two plausible priority rules and a sensitivity comparison.
6. A downloadable, reviewed **exercise** sitrep with owners and next update.'''),
code('''from fieldguide import district_map, priority_scores, sitrep, download_link
s=summarize(days=7)
display(s[["district","cases","reported_per_100k","completeness_pct","usable_beds"]].round(1))
district_map(s); plt.show()'''),
md('''## Inject 1 · A reporting interruption
At 09:00, the surveillance lead says Estuary's final-day report is missing. Is it already visible in the source table? Do not replace it with zero. Explain how this affects your confidence without estimating unobserved cases.'''),
code('''districts,reports,facilities=load_tables()
estuary_id=districts.loc[districts.district=="Estuary","district_id"].iloc[0]
display(reports.loc[(reports.district_id==estuary_id)&(reports.date>=pd.Timestamp("2025-11-25"))])'''),
md('''## Inject 2 · A changed planning assumption
At 10:00, a liaison asks you to give access delay more weight. Compare the new order with the baseline, then decide whether that change affects your verification calls. The rule is a discussion aid; local partners must review the recommendation.'''),
code('''a=priority_scores(s)
b=priority_scores(s,{"reported_burden":.2,"flood_exposure":.3,"access_delay":.5})
print("Baseline discussion order:",", ".join(a.head(3).district))
print("Access-focused order:",", ".join(b.head(3).district))
draft=sitrep(s)
display(download_link(draft,"capstone-exercise-draft.md","text/markdown"))'''),
md('''## Review rubric (0–2 points each)
| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Provenance | Source absent | Source named | Mode, source, cut-off and version |
| Reproducibility | Cannot recompute | Partial method | Inputs, code and period agree |
| Geographic reasoning | Misleading map | Basic map | Units, legend, table and limitations |
| Uncertainty | Hidden | Mentioned | Changes interpretation or verification |
| Decision usefulness | No next step | Vague action | Owner, due time and evidence |
| Accessibility | Visual only | Some text | Text/table and portable briefing |

**Completion standard for this workshop:** score at least 10/12 with no zero for provenance or uncertainty. This is an educational rubric, not professional certification.

## Facilitator debrief
Expected findings: the missing report must remain missing; population normalization changes the question; clinic availability must exclude nonfunctional sites; a live hazard feed does not establish a local health impact; changing weights can change the order. A strong team documents a defensible question and verification action even when it cannot resolve the uncertainty.''')],
"[WHO EOC framework](https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre) · [CDC Field Epidemiology Manual](https://www.cdc.gov/field-epi-manual/php/chapters/index.html).",
"Use lab 08 to package your final products. Ask another team to reproduce one indicator and challenge one assumption. Record the challenge, your revision and what remains unknown.")

print("Generated 12 guided notebooks.")
