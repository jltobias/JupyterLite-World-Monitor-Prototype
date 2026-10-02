# References, media and attributions

Links were reviewed while preparing this guide on **2 October 2026**. External services, documentation and videos can change. These are annotated learning resources; inclusion does not imply endorsement.

## Platform and implementation

1. **Elie Habib and World Monitor contributors.** [World Monitor source repository](https://github.com/koala73/worldmonitor) and [official documentation](https://www.worldmonitor.app/docs/documentation). Source for platform capabilities, flat-map/globe context and upstream attribution. The upstream code states AGPL-3.0-only; this guide does not redistribute the application code or imply branding rights.
2. **World Monitor.** [Sandbox guide](https://www.worldmonitor.app/docs/sandbox) and [public index](https://www.worldmonitor.app/sandbox/index.json). Source of four saved deterministic API examples. The saved subset excludes ACLED and is labeled as sample content.
3. **Project Jupyter contributors.** [JupyterLite documentation](https://jupyterlite.readthedocs.io/en/stable/) and [GitHub Pages deployment](https://jupyterlite.readthedocs.io/en/stable/howto/deployment/github-pages.html). Browser execution, content packaging and publication.
4. **Executable Books contributors.** [Jupyter Book 1 configuration](https://jupyter-book.readthedocs.io/v1/customize/config.html) and [execution configuration](https://jupyter-book.readthedocs.io/v1/content/execute.html). This guide pins the version-1 Python-based builder.
5. **Pyodide contributors.** [HTTP Python API](https://pyodide.org/en/stable/usage/api/python-api/http.html). Browser fetch implementation in the optional live lab.
6. **Folium contributors.** [Getting started](https://python-visualization.github.io/folium/latest/getting_started.html). Leaflet-backed Python maps.
7. **Plotly contributors.** [3D scatter in Python](https://plotly.com/python/3d-scatter-plots/). Interactive globe traces and HTML rendering.
8. **pandas contributors.** [Series.sum](https://pandas.pydata.org/docs/reference/api/pandas.Series.sum.html). `min_count` behavior used to preserve all-missing totals.

## Public-health and coordination context

9. **World Health Organization (2015).** [Framework for a Public Health Emergency Operations Centre](https://www.who.int/publications/i/item/framework-for-a-public-health-emergency-operations-centre). Context for coordinated information management and EOC practice. Our templates and rubrics are original exercises, not official forms.
10. **World Health Organization.** [Emergency operations](https://www.who.int/emergencies/operations). Context for EOC coordination and preparedness.
11. **Fontaine, R. E. / CDC (2024).** [Describing Epidemiologic Data](https://www.cdc.gov/field-epi-manual/php/chapters/describing-epi-data.html), *The CDC Field Epidemiology Manual*. Time, place, population and graphical interpretation. Our calculations and figures use original fictional data.
12. **CDC.** [Conducting a Field Investigation](https://www.cdc.gov/field-epi-manual/php/chapters/field-investigation.html) and [Designing and Conducting Analytic Studies in the Field](https://www.cdc.gov/field-epi-manual/php/chapters/design-conduct-analyze-field-studies.html). Investigation and hypothesis-testing context; descriptive overlap is not causal proof.

## Geographic and hazard sources

13. **Natural Earth contributors.** [Natural Earth terms of use](https://www.naturalearthdata.com/about/terms-of-use/) and [version 5.1.2 land GeoJSON](https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_110m_land.geojson). Public-domain 1:110m land polygons power the globe, world-map companion and hero geography. The hero layout and map renderings were created for this guide.
14. **U.S. Geological Survey.** [Earthquake GeoJSON summary format](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php). Optional live past-week M4.5+ feed and schema reference. The bundled earthquake-format events are invented, not USGS observations.
15. **OpenStreetMap contributors.** [Copyright and attribution](https://www.openstreetmap.org/copyright). Optional external basemap in the 2D lab; attribution remains visible in the map. No tiles are bundled.

## Video and original visual media

16. **WHO EIOS (2021).** [Global Technical Meeting, day 3 / track 2 / webinar 3](https://www.who.int/initiatives/eios/global-technical-meeting-2021/day3/webinar-3). Official session page with video and descriptions. Use it to discuss verification of intelligence signals; the notebook provides a reading prompt.
17. **WHO Science in 5 (2024).** [Episode 124: mpox — what you need to know](https://www.who.int/podcasts/episode/science-in-5/episode--124---mpox--what-you-need-to-know). Video and transcript used as a historical communication example, not current medical guidance. Media is linked, not copied.
18. **This repository's contributors (2026).** Hero SVG, workflow SVG, six chapter thumbnails, the [animated reporting timeline](../content/assets/reporting-timeline.gif), fictional CSVs, notebooks and briefing templates. Generated by the scripts in this repository. Figures label their synthetic source and provide numeric/text alternatives. No third-party logos or screenshots are presented as original work.

## How to cite the guide

> JupyterLite World Monitor Prototype contributors. (2026). *World Monitor / JupyterLite Field Guide*. GitHub repository. Include the commit identifier and access date when citing a specific version.

Use the source register and SHA-256 manifest to identify bundled reference assets. Provider data, code and media retain their respective terms; this reference page does not grant a blanket license over upstream material.
