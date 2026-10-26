![GeoDevelopment Observatory of Cambodia](images/og-image.jpg)

# GeoDevelopment Observatory of Cambodia (GDO-Cambodia)

**Website: [quarcs-lab.github.io/geo4cambodia](https://quarcs-lab.github.io/geo4cambodia/)**

The GeoDevelopment Observatory of Cambodia is a public-access platform for analyzing, monitoring, and evaluating **sustainable regional development** in Cambodia. It integrates environmental, social, and economic indicators from satellite imagery, household surveys, and administrative records (**GeoDevelopment Indicators**). It makes them explorable through AI-enhanced notebooks and web apps (**GeoDevelopment Tools**), and turns the results into accessible research summaries (**GeoDevelopment Insights**).

It serves:

* **Researchers**, who need ready-made subnational panels with reproducible code
* **Decision-makers**, who design, target, and evaluate regional policies
* **Citizens**, who want to understand development in their own province or district

---

## 📊 GeoDevelopment Indicators

| Module | Geography | Period | Join key | Files |
| --- | --- | --- | --- | --- |
| [`districts202-gdppc`](districts202-gdppc/) Estimated GDP per capita | 202 districts | 1990–2022 | `GID_2` | DTA · CSV · GeoJSON |
| [`provinces25-env`](provinces25-env/) Population, VIIRS-like lights, electricity-based GDP, NPP, PM2.5 | 25 provinces | 1990–2023 | `shapeISO` | CSV · DTA |
| [`provinces17-hdi`](provinces17-hdi/) Human development, income, DMSP-like lights, population | 17 GDL regions | 2013–2019 | `GDLcode` | CSV · DTA · GeoJSON |
| [`regionNames`](regionNames/) Identifiers and names for all three geographies | 17 · 25 · 202 | — | — | CSV |
| [`maps`](maps/) Boundary and panel GeoJSON files | 17 · 202 | — | — | GeoJSON |

Each folder has a `README.md` with a variable dictionary, example code, data sources, and a recommended citation. A combined dictionary is in [`definitions_gdo-cambodia.csv`](definitions_gdo-cambodia.csv).

```python
import geopandas as gpd

url = "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/maps/districts202_wide_y.geojson"
gdf = gpd.read_file(url)
gdf.plot(column="y2022", cmap="magma", scheme="quantiles", k=5, legend=True)
```

---

## 🐍 GeoDevelopment Tools

### Cloud-based notebooks

* **[Monitoring subnational human development](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/hdi_ntl_esda.ipynb)**: maps, trajectories, and spatial clusters of the Human Development Index and night-time lights.
* **[District GDP per capita: EDA](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_eda.ipynb)**: descriptive statistics and growth paths for 202 districts.
* **[District GDP per capita: ESDA](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_esda.ipynb)**: spatial weights, Moran's I, and LISA clusters.

### Web apps

* [Localized dynamics of luminosity-based GDP](https://carlos-mendez.projects.earthengine.app/view/egdp-dynamics-cambodia) (source in [`apps/`](apps/))
* [Comparative regional dynamics of luminosity-based GDP](https://carlos-mendez.projects.earthengine.app/view/space-time-dynamics-egdp-cambodia)
* [Land surface temperature, soil moisture and land cover](https://ee-yukietohjaxa.projects.earthengine.app/view/lst-smc-byregion)
* [Poverty mapping dashboard](https://cambodiapovertymapping.sig-gis.com/en/map/) (Spatial Informatics Group)

---

## 💡 GeoDevelopment Insights

* **Mapping Cambodian poverty with big data and AI**: Khoun, T., Poortinga, A., Thwal, N. S., González de Alba, I., McMahon, A., & Mendez, C. (2025). *Social Indicators Research*, 180(3), 1593–1618. [doi:10.1007/s11205-025-03718-3](https://doi.org/10.1007/s11205-025-03718-3)
* **Development studies in the age of AI**: video, podcast, and slides
* **The view from above**: an introductory video

All of these are on the [website](https://quarcs-lab.github.io/geo4cambodia/#insights), with embedded videos, audio, story books, and an AI chatbot.

---

## 📁 Repository structure

```
geo4cambodia/
├── index.html               # The website (React 18 + Tailwind, no build step)
├── 404.html, robots.txt, sitemap.xml, site.webmanifest, .nojekyll
├── districts202-gdppc/      # Indicator module (data + README)
├── provinces25-env/         # Indicator module
├── provinces17-hdi/         # Indicator module
├── regionNames/             # ID ↔ name lookups for each geography
├── maps/                    # GeoJSON boundaries and panels
├── notebooks/               # Colab notebooks (.ipynb) paired with MyST markdown (.md)
├── apps/                    # Earth Engine app source code
├── code/                    # Data-preparation scripts and links
├── media/                   # Audio files used on the site
├── images/                  # Site images (hero, logos, screenshots, people)
├── definitions_gdo-cambodia.csv
├── pyproject.toml, uv.lock  # Python environment (uv)
└── CITATION.cff, LICENSE, CLAUDE.md
```

### Run locally

```bash
uv sync                              # Python environment for the notebooks
uv run jupyter lab notebooks/        # open the notebooks
python3 -m http.server 8000          # preview the website at http://localhost:8000
```

The site is a single `index.html` with no build step. Every item (indicator, notebook, app, insight, event) is an entry in the `CONTENT_REGISTRY` array, and each entry gets a shareable detail page at `#/<section>/<id>`. GitHub Pages publishes the `main` branch directly.

---

## 👥 Team

**Core team:** [Carlos Mendez](https://carlos-mendez.org) (Nagoya University, Japan) · Theara Khoun (UNDP Cambodia) · Ate Poortinga (Spatial Informatics Group, USA)
**Research associates:** [Li Xiaomeng](https://carlos-mendez.org/authors/lixiaomeng/) (Nagoya University, Japan) · [He Du](https://carlos-mendez.org/authors/hedu/) (Nagoya University, Japan)

**Contact:** [carlos.mendez.n9@f.mail.nagoya-u.ac.jp](mailto:carlos.mendez.n9@f.mail.nagoya-u.ac.jp) · [theara.khoun@undp.org](mailto:theara.khoun@undp.org) · [apoortinga@sig-gis.com](mailto:apoortinga@sig-gis.com)
**Community:** [GitHub Discussions](https://github.com/quarcs-lab/geo4cambodia/discussions)

---

## 📝 Citation

> Mendez, C., Khoun, T., & Poortinga, A. (2026). *GeoDevelopment Observatory of Cambodia*. https://quarcs-lab.github.io/geo4cambodia/

```bibtex
@misc{gdocambodia2026,
  author       = {Mendez, Carlos and Khoun, Theara and Poortinga, Ate},
  title        = {{GeoDevelopment Observatory of Cambodia}},
  year         = {2026},
  howpublished = {\url{https://quarcs-lab.github.io/geo4cambodia/}},
  note         = {Data and code: https://github.com/quarcs-lab/geo4cambodia}
}
```

---

**Disclaimer.** The indicators, tools, and insights are the responsibility of the individual researchers and do not necessarily represent the views of their affiliated institutions or related organizations. Maps are for geo-statistical use only; they have a referential, informational character and do not represent an official definition of Cambodia's territorial boundaries.

**License.** Code and data in this repository: [MIT](LICENSE). Original data sources are credited in each module's README. Hero and section illustrations were generated with OpenAI image generation (via Codex).
