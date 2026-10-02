"""Regenerate ONLY fictional exercise data; never fetch live observations."""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content" / "data"
DATA.mkdir(parents=True, exist_ok=True)
rng = random.Random(42)


def write_csv(name, rows):
    with (DATA / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


districts, features, reports, facilities = [], [], [], []
names = ["Harbor", "Estuary", "Lagoon", "Riverbend", "Central", "Palms", "Highland", "Orchard", "Plateau"]
for i, name in enumerate(names):
    col, row = i % 3, i // 3
    lon, lat = 34.5 + col * .4, -19.4 + row * .4
    population = [42000, 78000, 31000, 65000, 120000, 53000, 26000, 48000, 36000][i]
    flood = [72, 85, 55, 42, 26, 33, 8, 12, 5][i]
    districts.append(dict(district_id=f"D{i+1:02}", district=name, population=population,
                          longitude=lon+.2, latitude=lat+.2, flood_pct=flood))
    ring = [[lon, lat], [lon+.4, lat], [lon+.4, lat+.4], [lon, lat+.4], [lon, lat]]
    features.append(dict(type="Feature", properties=districts[-1], geometry=dict(type="Polygon", coordinates=[ring])))
    facilities.append(dict(facility_id=f"F{i+1:02}", district_id=f"D{i+1:02}", facility=f"{name} training clinic",
                           longitude=lon+.15, latitude=lat+.25, beds=20+i*5,
                           available_beds=max(0, 12+i*3-(10 if i < 3 else 0)),
                           functional=int(i not in (1, 3)), access_delay_hours=[8,24,6,18,2,4,1,2,1][i]))
    for day in range(28):
        expected = 5
        received = (max(1, expected-rng.randint(1,3)) if i < 4 and day > 17 else expected)
        received = 0 if i == 1 and day == 27 else received
        pulse = max(0, 1-abs(day-20)/10)
        count = round((population/15000 + pulse*flood/4) * received/expected + rng.random()*3)
        reports.append(dict(date=str(date(2025,11,1)+timedelta(days=day)), district_id=f"D{i+1:02}",
                            cases_reported=count if received else "", reports_received=received,
                            reports_expected=expected, rainfall_mm=round(max(0, 45-abs(day-12)*5)+rng.random()*6,1)))

write_csv("districts.csv", districts)
write_csv("surveillance.csv", reports)
write_csv("facilities.csv", facilities)
(DATA / "districts.geojson").write_text(json.dumps(dict(type="FeatureCollection", features=features),indent=2)+"\n",encoding="utf-8")
hazards = [
    ("H01", "Pacific exercise", -75, -12, 5.8), ("H02", "Island exercise", 140, 36, 4.9),
    ("H03", "Rift exercise", 36, -2, 4.5), ("H04", "Atlantic exercise", -28, 38, 5.1),
    ("H05", "Coastal exercise", 35, -19, 4.7), ("H06", "Mountain exercise", 86, 28, 5.6),
    ("H07", "Northern exercise", -150, 62, 4.6), ("H08", "Southern exercise", 172, -42, 5.3),
]
fc = dict(type="FeatureCollection", metadata=dict(title="SYNTHETIC earthquake-format exercise", generated=1764374400000),
          features=[dict(type="Feature", id=id, properties=dict(place=place, mag=mag, time=1764288000000+i*3600000,
                        url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php"),
                        geometry=dict(type="Point", coordinates=[lon,lat,10+i*5])) for i,(id,place,lon,lat,mag) in enumerate(hazards)])
(DATA / "earthquakes_training.geojson").write_text(json.dumps(fc,indent=2)+"\n", encoding="utf-8")
print("Wrote fictional districts, surveillance, facilities and earthquake-format events (seed 42).")
