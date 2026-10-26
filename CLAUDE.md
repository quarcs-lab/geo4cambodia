# Working with Claude on GDO-Cambodia

This guide helps you work effectively with Claude (AI assistant) on the GeoDevelopment Observatory of Cambodia: analyzing the data, extending the notebooks, and updating the website.

## Quick start prompts

```
"Load the district GDP per capita panel and map the average annual growth
rate 1990-2022 with a quantile classification."
```

```
"Compute Moran's I and a LISA cluster map for trend400_ln_y in 2022 using
queen contiguity on maps/districts202.geojson."
```

```
"Add a new indicator module for <dataset>, following the README template of
districts202-gdppc, and register it on the website."
```

## Project structure

- **`index.html`**: the entire website (React 18 UMD + Babel standalone + Tailwind Play CDN, all pinned). There is no build step.
- **`districts202-gdppc/`**: GDP per capita for 202 districts, 1990–2022 (key `GID_2` / `id`)
- **`provinces25-env/`**: population, VIIRS-like lights, electricity-based GDP, NPP and PM2.5 for 25 provinces (key `shapeISO`)
- **`provinces17-hdi/`**: HDI, GNI, DMSP-like lights and population for 17 Global Data Lab regions (key `GDLcode` / `id`)
- **`regionNames/`**: ID ↔ name lookups for all three geographies
- **`maps/`**: GeoJSON boundaries and wide panels (CRS84)
- **`notebooks/`**: Colab notebooks paired with MyST `.md` files through jupytext
- **`apps/`**: Google Earth Engine app source (`.js`)
- **`code/`**: data-preparation scripts and links
- **`media/`**, **`images/`**: site assets

## Environment setup (uv)

```bash
uv sync                                    # install dependencies
uv run jupyter lab notebooks/              # open notebooks
uv run jupytext --sync notebooks/*.ipynb   # re-pair after editing a notebook
uv add <package>                           # add a dependency (commit uv.lock)
python3 -m http.server 8000                # preview the website locally
```

- Always use `uv run` for Python and Jupyter.
- Commit `uv.lock` after changing dependencies. Never commit `.venv/`.
- The notebooks keep their `!pip install` cells for Google Colab. They are harmless locally.

## Key identifiers: three geographies

There is **no single universal key**. Use the key that belongs to each geography:

| Geography | Units | Key | Module |
| --- | --- | --- | --- |
| Global Data Lab regions | 17 | `GDLcode` (or `id`) | `provinces17-hdi` |
| Provinces (geoBoundaries ADM1) | 25 | `shapeISO` (or `shapeID`) | `provinces25-env` |
| Districts (GADM level 2) | 202 | `GID_2` (or `id`) | `districts202-gdppc` |

Province names are spelled differently in each source. Harmonize them before merging across geographies.

Known data issue: `provinces25-env/total_NPP` is all zeros in the current release. Treat it as missing.

## Loading data

```python
import pandas as pd, geopandas as gpd
BASE = "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/"
df  = pd.read_stata(BASE + "districts202-gdppc/cambodia202-1990-2022-GDPpc.dta")   # long panel
gdf = gpd.read_file(BASE + "maps/districts202.geojson")                            # boundaries
gdf = gdf.merge(df.query("year == 2022"), on="GID_2")
```

## Updating the website

All content is data in the `CONTENT_REGISTRY` array in `index.html`. To add an item:

1. Add an object with `id`, `type` (`indicator` | `notebook` | `app` | `insight` | `event`), `section` (`indicators` | `tools` | `insights` | `events`), `title`, `summary`, `description`, `tags`, `image`, `imageAlt`, `date` and `pinned`, plus the type-specific fields. Copy an existing entry of the same type.
2. Put images in `images/<section>/` as WebP, at most 1600 px wide.
3. The item automatically gets a card and a shareable detail page at `#/<section>/<id>`.
4. For a new indicator, also add a `Dataset` entry to the JSON-LD block in `<head>`, and a row to `definitions_gdo-cambodia.csv`.

Design tokens are defined in `tailwind.config`: `navy-950…500`, `brand-red` (#d23c3c), `brand-sky` (#7cc4ff). Keep text contrast at WCAG AA or better, keep `prefers-reduced-motion` working, and give every image meaningful `alt` text.

## Preferred libraries

pandas, geopandas, libpysal, esda, splot, mapclassify, mgwr, inequality, statsmodels, matplotlib, seaborn, plotly.
