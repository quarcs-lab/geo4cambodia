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

All data share one spatial backbone. Every unit at every scale has a **geo ID** that nests by prefix (GADM 4.1 hierarchy): district `KH-16-01` lies in province `KH-16`, which lies in Cambodia `KH`. Global Data Lab regions (`KH-GDL-08`) are unions of whole provinces. Datasets are panels with one row per unit (`geo_id`) and year, published as CSV and Parquet.

| Dataset | Title | Scale | Period | Files |
| --- | --- | --- | --- | --- |
| [`gdppc`](docs/datasets/gdppc.md) | Estimated GDP per capita | 202 districts | 1990–2022 | [`data/district/gdppc`](data/district/) |
| [`env`](docs/datasets/env.md) | Population, VIIRS-like lights, electricity-based GDP, NPP, PM2.5 | 25 provinces | 1986–2023 | [`data/province/env`](data/province/) |
| [`hdi`](docs/datasets/hdi.md) | Human development, income, DMSP-like lights, population | 17 GDL regions | 2013–2019 | [`data/gdl/hdi`](data/gdl/) |
| [`geo`](geo/) | Units, names, boundaries and crosswalks for every scale | 245 units | — | [`geo/`](geo/) |

Each dataset has a [Frictionless datapackage](metadata/) and a generated page in [`docs/datasets/`](docs/datasets/) with its variable dictionary, coverage, sources and citation. All variables are listed in [`definitions_gdo-cambodia.csv`](definitions_gdo-cambodia.csv). **How the database works, and how to build your own indicators:** [`docs/data-infrastructure.md`](docs/data-infrastructure.md).

### Load the data: two ways

**With the package** ([`geo4cambodia`](docs/python-package.md); in Colab `!pip install geo4cambodia -q`):

```python
import geo4cambodia as geo

geo.datasets()                                       # what is available, at which scale and years
geo.dictionary("gdppc")                              # variables, units, aggregation rules
gdf = geo.load("gdppc", years=2022, geometry=True)   # panel + district boundaries
gdf.plot(column="y", cmap="magma", scheme="quantiles", k=5, legend=True)

geo.aggregate(geo.load("env"), to="gdl", dataset="env")    # provinces -> GDL regions (metadata rules)
geo.combine(["env", "hdi"], scale="gdl")                   # two datasets, one scale
```

**Without the package**: every file is a plain URL, for pandas, R, Stata or Excel.

```python
import pandas as pd, geopandas as gpd
BASE = "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/"
df = pd.read_csv(BASE + "data/district/gdppc.csv")                   # geo_id, year, variables
units = pd.read_csv(BASE + "geo/units.csv")                           # names, parents, source codes
gdf = gpd.read_file(BASE + "geo/boundaries/district.geojson")         # polygons keyed by geo_id
```

### Build your own indicators

The package also links your own tables to the same units (by names in any spelling or by codes), extracts indicators from rasters, moves data onto grids, and saves results in the same documented format:

```python
mine = geo.link(my_table, scale="province", on="Province")        # "BântéayMéanchey" -> KH-01
ntl = geo.zonal("viirs_2020.tif", scale="district", name="ntl", year=2020)
geo.save(mine, "my_indicator", scale="province", directory="my_data")
gdf, df, df_dict = geo.for_geometrics("gdppc")                       # inputs for geometrics
```

To add a dataset to the observatory, see [`CONTRIBUTING_DATA.md`](CONTRIBUTING_DATA.md).

---

## 🐍 GeoDevelopment Tools

### Python packages

* **[geo4cambodia](docs/python-package.md)** (`pip install geo4cambodia`): load every indicator as a panel with boundaries, link your own data, extract indicators from rasters, and move data across scales.
* **[geometrics](https://quarcs-lab.github.io/geometrics/)** (`pip install geometrics`): regional growth, convergence and inequality with spatial methods. `geo.for_geometrics()` prepares the observatory's data for it in one line.

### Cloud-based notebooks

* **[Load, link and build indicators with geo4cambodia](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb)**: load data with and without the package, move it across scales, link your own table, and build an indicator from a raster.
* **[Are Cambodia's districts converging?](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb)**: geo4cambodia + geometrics: LISA clusters and β-, σ- and club convergence, plus inequality between and within provinces.
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
├── data/<scale>/            # Published panels: <dataset>.csv + .parquet (generated)
├── geo/                     # Spatial backbone: scales.yaml, units, boundaries/, crosswalks/
├── metadata/                # One Frictionless datapackage per dataset (source of truth for docs)
├── project.yaml             # Project identity: name, package, repository, country codes (read by the package)
├── raw/                     # Original inputs, never edited; `geo4cambodia build` regenerates everything from them
├── src/geo4cambodia/        # Python package: load, link, zonal, aggregate, overlay, combine, save, build, validate
├── tests/                   # test_core.py (generic) + test_project.py (Cambodia facts)
├── scripts/                 # new_project.py: start a geo4<country> project from this template
├── notebooks/               # Colab notebooks (.ipynb) paired with MyST markdown (.md)
├── apps/                    # Earth Engine app source code
├── code/                    # Pointers to data-preparation code
├── media/, images/          # Site assets
├── definitions_gdo-cambodia.csv   # All variables of all datasets (generated)
├── docs/                    # data-infrastructure.md, python-package.md (PyPI page), publishing.md, datasets/
├── CONTRIBUTING_DATA.md     # How to add a dataset or a scale
├── TEMPLATE.md              # How to reuse this repository for another country
├── pyproject.toml, uv.lock  # Python package and environment (uv)
└── CITATION.cff, LICENSE, CLAUDE.md
```

### Run locally

```bash
uv sync                          # environment + the geo4cambodia package (editable)
uv run geo4cambodia build        # regenerate data/, geo/, docs/ from raw/
uv run geo4cambodia validate     # check IDs, schemas, nesting and file consistency
uv run pytest                    # run the test suite
uv run jupyter lab notebooks/    # open the notebooks
python3 -m http.server 8000      # preview the website at http://localhost:8000
```

Release the package on PyPI with [`docs/publishing.md`](docs/publishing.md).

### A template for other countries

This repository is also the template of a family of `geo4<country>` projects that share one design: geo IDs, long panels, Frictionless metadata, and the same package API. `python scripts/new_project.py ../geo4laos --package geo4laos --country Laos --iso2 LA --iso3 LAO --repo my-org/geo4laos` creates a new project. All project-specific settings live in `project.yaml`. See [`TEMPLATE.md`](TEMPLATE.md).

### The website

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

**License.** Code and data in this repository: [MIT](LICENSE). Original data sources are credited in each dataset's page in `docs/datasets/`. Hero and section illustrations were generated with OpenAI image generation (via Codex).
