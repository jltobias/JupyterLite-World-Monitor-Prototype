# Data dictionary and provenance

## Three distinct data modes

| Mode | Files / surface | Meaning |
|---|---|---|
| Synthetic training | `districts.csv`, `districts.geojson`, `surveillance.csv`, `facilities.csv`, `earthquakes_training.geojson` | Invented examples, not observations |
| Upstream sandbox | `worldmonitor/*.json` | Deterministic World Monitor API examples retrieved 2026-10-02 |
| Reference geography | `ne_110m_land.geojson` | Natural Earth v5.1.2 land polygons, 1:110 million scale |
| Optional live | World Monitor embed; USGS past-week M4.5+ feed | External content only when explicitly opened/requested |

`provenance.json` records exact reference-asset URLs, retrieval dates and SHA-256 hashes. `scripts/make_training_data.py` regenerates synthetic files using Python's seeded random generator (`42`); it does not fetch real observations. The source files are committed for reproducibility. Clinical and public-health conclusions cannot be drawn from these invented values.

## Fictional coastal-health exercise

Nine rectangular districts are placed between 34.5–35.7° E and 19.4–18.2° S for coordinate teaching. The names and boundaries are fictional. They do not represent administrative areas, facility locations or disease burden in Mozambique or any other country. Dates span 1–28 November 2025; the common analysis window is 22–28 November inclusive. Dates are calendar reporting days in UTC.

The generator creates a rise in reports related to a chosen flood-exposure parameter and reduces reporting completeness in selected districts. These built-in associations are teaching devices. They are not empirical evidence.

### Districts

| Field | Type / unit | Interpretation |
|---|---|---|
| `district_id` | string, D01–D09 | Stable join key; unique |
| `district` | text | Invented district name |
| `population` | integer persons | Positive, fixed resident denominator |
| `longitude`, `latitude` | decimal degrees, WGS84-style coordinates | Center of fictional grid cell |
| `flood_pct` | percent, 0–100 | Fictional share of resident population exposed to flood |

The GeoJSON repeats these properties and contains closed polygon rings in longitude, latitude order. No area calculation is made in degrees.

### Surveillance

| Field | Type / unit | Interpretation |
|---|---|---|
| `date` | YYYY-MM-DD | Report day, not symptom onset |
| `district_id` | string | Join key to districts |
| `cases_reported` | integer or empty | New suspected-syndrome reports received that day |
| `reports_received` | integer, 0–5 | Reporting submissions received |
| `reports_expected` | integer, 5 | Expected submissions per district/day |
| `rainfall_mm` | decimal millimeters/day | Synthetic environmental context; not used to infer causation |

There is exactly one row per district/day (252 rows). **Empty case count means missing**, not zero; Estuary's final day intentionally has no received reports. Partial reporting produces observed counts with incomplete coverage. No patient records or personal identifiers exist. The fixture assumes no duplicate cases within the submitted counts; real surveillance needs explicit case deduplication and revision handling.

### Facilities

| Field | Type / unit | Interpretation |
|---|---|---|
| `facility_id`, `district_id` | strings | Unique facility and district join keys |
| `facility` | text | Invented training clinic |
| `longitude`, `latitude` | decimal degrees | Invented point position |
| `beds` | integer beds | Nominal capacity |
| `available_beds` | integer beds | Available beds before functional-status check |
| `functional` | 0 or 1 | Exercise operating status |
| `access_delay_hours` | hours | Invented delay; not a computed route/travel-time estimate |

One clinic per district is a deliberate simplification. `usable_beds = available_beds × functional`; bed availability is not a comprehensive measure of care capability.

## Derived measures

- **Reported cases per 100,000, over N days:** sum of newly reported cases in the inclusive window / resident population × 100,000. This is an observed reporting measure, not an estimate of infection incidence or person-time rate.
- **Completeness (%):** total received reports / total expected reports × 100. Aggregate using the sums, not an unweighted mean if expectations differ.
- **Exercise score:** 100 × [0.5 × clipped(reports per 100,000 / 300) + 0.3 × flood_pct / 100 + 0.2 × clipped(access_delay_hours / 24)]. Clipping is to [0,1]. Anchors and weights are arbitrary classroom assumptions, not validated thresholds.
- **Population sensitivity bars:** recompute the reported-case measure at 0.8 and 1.2 times the population. These are scenario bounds, not confidence intervals.

## Hazard-format examples

`earthquakes_training.geojson` follows the subset of the USGS GeoJSON shape needed by the labs: event ID; magnitude; place; time in Unix milliseconds; Point coordinates `[longitude, latitude, depth_km]`. All eight events are invented. The metadata's generated time is an exercise timestamp. The optional live adapter records actual retrieval time separately and never labels this fixture live.

## Sources and permitted interpretation

Natural Earth supplies small-scale public-domain geography; it is not a navigation dataset. The [terms page](https://www.naturalearthdata.com/about/terms-of-use/) documents its status. World Monitor fixtures retain their upstream envelopes and source attribution; see [sandbox documentation](https://www.worldmonitor.app/docs/sandbox) and the [upstream project](https://github.com/koala73/worldmonitor). The interactive map's optional background is attributed to [OpenStreetMap contributors](https://www.openstreetmap.org/copyright). Consult provider terms when adapting these resources; this repository does not relicense upstream material.
