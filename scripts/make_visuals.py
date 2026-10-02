"""Render original teaching graphics from the bundled data (no network)."""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"content"))
from fieldguide import load_tables, summarize, district_map, land_rings, priority_scores, setup_style

OUT=ROOT/"content/assets"
OUT.mkdir(exist_ok=True)
setup_style()
s=summarize()
districts,reports,facilities=load_tables()


def save(fig,name):
    fig.savefig(OUT/name,dpi=130,bbox_inches="tight",facecolor="white")
    plt.close(fig)


save(district_map(s),"map2d.png")
fig=plt.figure(figsize=(8,6)); ax=fig.add_subplot(projection="3d")
for ring in land_rings():
    lon=np.deg2rad(ring[:,0]); lat=np.deg2rad(ring[:,1])
    ax.plot(np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat),color="#007f86",linewidth=.6)
ax.set_axis_off(); ax.set_box_aspect([1,1,1]); ax.view_init(elev=20,azim=25)
ax.set_title("Geographic context · Natural Earth globe",pad=0)
save(fig,"globe.png")
daily=reports.groupby("date").agg(cases=("cases_reported","sum"),received=("reports_received","sum"),expected=("reports_expected","sum"))
fig,axes=plt.subplots(2,1,figsize=(8,5),sharex=True)
axes[0].bar(daily.index,daily.cases,width=1,color="#007f86"); axes[0].set(ylabel="Reports",title="SYNTHETIC · Read the curve with its coverage")
axes[1].plot(daily.index,100*daily.received/daily.expected,color="#db5b45"); axes[1].set(ylabel="Coverage (%)",ylim=(0,105))
fig.autofmt_xdate(); fig.tight_layout(); save(fig,"epi.png")
q=reports.assign(pct=100*reports.reports_received/reports.reports_expected).pivot(index="district_id",columns="date",values="pct")
fig,ax=plt.subplots(figsize=(8,5)); im=ax.imshow(q,cmap="cividis",vmin=0,vmax=100,aspect="auto")
ax.set_yticks(range(9),districts.district); ax.set_xticks([0,7,14,21,27],["1 Nov","8 Nov","15 Nov","22 Nov","28 Nov"])
ax.set_title("SYNTHETIC · Make reporting gaps visible"); fig.colorbar(im,ax=ax,label="Reports received (%)")
fig.tight_layout(); save(fig,"quality.png")
r=priority_scores(s); fig,ax=plt.subplots(figsize=(8,5)); left=np.zeros(len(r))
for field,w in {"reported_burden":.5,"flood_exposure":.3,"access_delay":.2}.items():
    values=r[field].to_numpy()*w*100; ax.barh(r.district,values,left=left,label=field.replace("_"," ")); left+=values
ax.invert_yaxis(); ax.set(xlabel="Exercise score, not a validated risk model",title="SYNTHETIC · Explain the priority discussion"); ax.legend(fontsize=8)
fig.tight_layout(); save(fig,"planning.png")
fig,ax=plt.subplots(figsize=(8,5)); ax.set_axis_off()
ax.text(0,1,"TRAINING / SITUATION REPORT",fontsize=18,weight="bold",color="#132c46",va="top")
ax.text(0,.84,"22–28 NOV 2025  •  NINE FICTIONAL DISTRICTS",fontsize=10,color="#007f86")
for y,title,desc in [( .65,"01  CURRENT PICTURE","What was observed · source · time · place"),(.44,"02  ASSESSMENT & GAPS","What it may mean · what remains uncertain"),(.23,"03  ACTION & NEXT UPDATE","Owner · due time · verification evidence")]:
    ax.text(0,y,title,fontsize=14,weight="bold",color="#132c46"); ax.text(0,y-.09,desc,fontsize=11,color="#536579")
ax.text(0,.02,"Markdown + HTML + CSV + map + provenance",fontsize=10,color="#007f86")
save(fig,"sitrep.png")

# Original animated teaching media; a text description appears in lab 10.
fig,axes=plt.subplots(2,1,figsize=(7,4),sharex=True)
def frame(k):
    for ax in axes: ax.clear()
    selected=daily.iloc[:k+1]
    axes[0].bar(selected.index,selected.cases,width=1,color="#007f86")
    axes[0].set(ylabel="Reports",ylim=(0,daily.cases.max()*1.1),title="SYNTHETIC EXERCISE · Reports and completeness")
    axes[1].plot(selected.index,100*selected.received/selected.expected,color="#db5b45",linewidth=2)
    axes[1].set(ylabel="Coverage (%)",ylim=(0,105),xlim=(daily.index.min(),daily.index.max()))
    fig.autofmt_xdate(); fig.tight_layout()
animation=FuncAnimation(fig,frame,frames=list(range(0,28,2))+[27],interval=300)
animation.save(OUT/"reporting-timeline.gif",writer=PillowWriter(fps=3),dpi=85)
plt.close(fig)

# Vector hero: actual land outlines in orthographic projection, original layout.
paths=[]
for ring in land_rings():
    lon=np.deg2rad(ring[:,0]-25); lat=np.deg2rad(ring[:,1]); lat0=np.deg2rad(15)
    visible=np.sin(lat0)*np.sin(lat)+np.cos(lat0)*np.cos(lat)*np.cos(lon)>0
    x=1170+265*np.cos(lat)*np.sin(lon)
    y=325-265*(np.cos(lat0)*np.sin(lat)-np.sin(lat0)*np.cos(lat)*np.cos(lon))
    active=False; points=[]
    for xx,yy,ok in zip(x,y,visible):
        if ok:
            points.append(f'{"L" if active else "M"}{xx:.1f},{yy:.1f}'); active=True
        else: active=False
    paths.append(f'<path d="{" ".join(points)}"/>')
land="".join(paths)
hero=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="840" viewBox="0 0 1600 840" role="img" aria-labelledby="title desc">
<title id="title">World Monitor / JupyterLite Field Guide</title><desc id="desc">From global signals to shared understanding. A geographic globe, learning routes and small synthetic example charts introduce a guide for global health and emergency operations.</desc>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#071b2e"/><stop offset="1" stop-color="#123b4b"/></linearGradient><radialGradient id="sea"><stop stop-color="#1c5468"/><stop offset="1" stop-color="#082338"/></radialGradient><clipPath id="globe"><circle cx="1170" cy="325" r="265"/></clipPath></defs>
<rect width="1600" height="840" rx="20" fill="url(#bg)"/>
<g stroke="#568795" opacity=".16"><path d="M0 160H1600M0 320H1600M0 480H1600M0 640H1600M200 0V840M400 0V840M600 0V840M800 0V840M1000 0V840M1200 0V840M1400 0V840"/></g>
<g font-family="Segoe UI,Arial,sans-serif"><text x="72" y="78" font-size="20" letter-spacing="3" fill="#7ee0d1">WORLD MONITOR / JUPYTERLITE</text>
<rect x="72" y="113" width="213" height="35" rx="17" fill="#234956"/><text x="90" y="137" font-size="14" letter-spacing="2" fill="#d8eeee">AN OPEN FIELD GUIDE</text>
<text x="68" y="231" font-size="64" font-weight="700" fill="#f2f7f9">From global signals</text>
<text x="68" y="309" font-size="64" font-weight="700" fill="#f2f7f9">to shared</text>
<text x="68" y="387" font-size="64" font-weight="700" fill="#7ee0d1">understanding.</text>
<text x="72" y="453" font-size="24" fill="#c2d8e2">A browser-based learning lab for global health</text>
<text x="72" y="489" font-size="24" fill="#c2d8e2">and emergency operations.</text>
<text x="72" y="550" font-size="17" letter-spacing="1" fill="#f1be78">OBSERVE  /  VERIFY  /  MAP  /  EXPLAIN  /  ACT</text>
<circle cx="1170" cy="325" r="279" fill="none" stroke="#3c7c8b" stroke-dasharray="3 10"/>
<circle cx="1170" cy="325" r="265" fill="url(#sea)" stroke="#589aaa"/>
<g clip-path="url(#globe)" fill="none" stroke="#7ee0d1" stroke-width="1.4" opacity=".8">{land}</g>
<g fill="#f1be78" stroke="#fff3da" stroke-width="2"><circle cx="1233" cy="308" r="7"/><circle cx="1103" cy="238" r="6"/><circle cx="1242" cy="451" r="8"/></g>
<path d="M1103 238Q1280 180 1242 451" fill="none" stroke="#f1be78" stroke-dasharray="6 6" opacity=".7"/>
<rect x="1067" y="559" width="212" height="32" rx="16" fill="#234956"/><text x="1088" y="581" font-size="13" letter-spacing="1" fill="#dbebec">ILLUSTRATIVE SIGNALS</text>
<g fill="#102f42" stroke="#376074"><rect x="72" y="633" width="464" height="137" rx="12"/><rect x="568" y="633" width="464" height="137" rx="12"/><rect x="1064" y="633" width="464" height="137" rx="12"/></g>
<text x="96" y="671" fill="#7ee0d1" font-size="14" letter-spacing="2">01 / EXPLORE</text><text x="96" y="707" fill="#fff" font-size="26" font-weight="600">Maps with context</text><text x="96" y="741" fill="#bed4df" font-size="17">2D layers · 3D globe · spatial reasoning</text>
<text x="592" y="671" fill="#7ee0d1" font-size="14" letter-spacing="2">02 / UNDERSTAND</text><text x="592" y="707" fill="#fff" font-size="26" font-weight="600">Evidence you can inspect</text><text x="592" y="741" fill="#bed4df" font-size="17">12 Python labs · uncertainty · provenance</text>
<text x="1088" y="671" fill="#7ee0d1" font-size="14" letter-spacing="2">03 / SHARE</text><text x="1088" y="707" fill="#fff" font-size="26" font-weight="600">A clearer situation report</text><text x="1088" y="741" fill="#bed4df" font-size="17">Open book · live notebooks · briefing ZIP</text>
<text x="72" y="811" fill="#94b5c3" font-size="14">Independent educational companion • Synthetic health exercises • Natural Earth geography</text></g></svg>'''
(OUT/"hero.svg").write_text(hero,encoding="utf-8")
steps=[("OBSERVE","Signals + source"),("VERIFY","Time + coverage"),("ANALYZE","Maps + methods"),("BRIEF","Claim + uncertainty"),("REVIEW","Owner + next step")]
items=[]
for i,(title,desc) in enumerate(steps):
    x=20+i*235
    items.append(f'<rect x="{x}" y="30" width="215" height="110" rx="12" fill="#123b4b"/><text x="{x+18}" y="70" font-size="18" fill="#7ee0d1">{i+1:02} / {title}</text><text x="{x+18}" y="108" font-size="16" fill="#ffffff">{desc}</text>')
    if i<4: items.append(f'<text x="{x+218}" y="92" fill="#007f86" font-size="23">→</text>')
(OUT/"workflow.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="170" viewBox="0 0 1200 170" role="img"><title>Observe, verify, analyze, brief, review</title><g font-family="Segoe UI,Arial,sans-serif">'+''.join(items)+'</g></svg>',encoding="utf-8")
print("Rendered hero, workflow, six thumbnails and animated timeline.")
