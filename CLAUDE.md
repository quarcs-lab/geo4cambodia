# Working with Claude on GDO-Cambodia

This guide helps you work effectively with Claude (AI assistant) on the GeoDevelopment Observatory of Cambodia: analysing the data, building indicators with the `geo4cambodia` package, extending the notebooks, and updating the website.

This repository is also the **reference template** for a family of `geo4<country>` projects (see `TEMPLATE.md`). Keep generic code generic: it must never hard-code Cambodia, the repository or the package name.

## Read first

| File | What it explains |
| --- | --- |
| `docs/data-infrastructure.md` | How the indicators database works: scales, geo IDs, units, metadata, aggregation rules, loading with and without the package, recipes for building indicators, the package reference |
| `CONTRIBUTING_DATA.md` | Step by step: add a dataset or a spatial scale |
| `TEMPLATE.md` | What is generic and what is project-specific; starting a new country project |
| `docs/python-package.md` | The package's PyPI page (absolute links only) |
| `docs/publishing.md` | Releasing the package on PyPI |

## Quick start prompts

```
"Load the district GDP per capita panel with geo4cambodia and map the average
annual growth rate 1990-2022 with a quantile classification."
```

```
"Use geo.for_geometrics('gdppc') and geometrics to test beta-convergence with a
spatial Durbin model and map the convergence clubs."
```

```
"Add a new dataset at the province scale from raw/<dataset>/, following
CONTRIBUTING_DATA.md, and register it on the website."
```

## Project structure

- **`project.yaml`**: project identity. Holds the name, the package name, the GitHub repository and default ref, the country codes (`KH`, `KHM`), the equal-area CRS and the catalog file name. It is bundled into the wheel.
- **`index.html`**: the entire website (React 18 UMD + Babel standalone + Tailwind Play CDN, all pinned). There is no build step.
- **`raw/`**: original inputs. Never edit them; fixes belong in the builders.
- **`geo/`**: the spatial backbone.
  - `scales.yaml`: the scale registry, edited by hand.
  - `units.csv/.parquet`, `boundaries/<scale>.geojson/.parquet`, `crosswalks/<from>__<to>.csv`: generated.
- **`data/<scale>/<dataset>.csv/.parquet`**: published panels, one row per `geo_id` × `year`. Generated.
- **`metadata/<dataset>.datapackage.json`** + `metadata/index.json`: Frictionless metadata, the source of truth for variables, units, sources and aggregation rules (`geo:` properties).
- **`docs/datasets/*.md`**, **`data/README.md`**, **`definitions_gdo-cambodia.csv`**: generated from the metadata.
- **`src/geo4cambodia/`**: the Python package.

  | Module | Kind | Contents |
  | --- | --- | --- |
  | `project.py` | generic | reads `project.yaml`, finds the local checkout |
  | `store.py` | generic | reads files locally or from GitHub |
  | `scales.py` | generic | the scale registry |
  | `metadata.py` | generic | reads the datapackages |
  | `io.py` | generic | `load`, `units`, `boundaries`, `crosswalk`, `datasets`, `dictionary` |
  | `create.py` | generic | `link`, `check`, `combine`, `zonal`, `save` |
  | `bridge.py` | generic | `for_expdpy`, `for_geometrics` |
  | `aggregate.py` | generic | `aggregate`, `overlay`, `overlay_weights` |
  | `validate.py` | generic | the validator |
  | `cli.py` | generic | the command line |
  | `build/common.py`, `build/gadm.py` | generic | writing data, docs and `geo/`; geography from any GADM file |
  | `build/geo.py`, `build/<dataset>.py` | Cambodia-specific | the builders |
  | `build/_template.py`, `build/_geo_template.py` | templates | starting points for new builders |

- **`tests/test_core.py`**: generic tests, driven by the registry and metadata. **`tests/test_project.py`**: Cambodia facts.
- **`scripts/new_project.py`** + `scripts/template/*.tpl`: create a new `geo4<country>` project.
- **`notebooks/`**: Colab notebooks paired with MyST `.md` files through jupytext.
  - `geo4cambodia_quickstart`: load, link and build indicators.
  - `expdpy_explore`, `expdpy_analyze`: panel exploration and econometrics with expdpy.
  - `geometrics_convergence`: spatial analysis with geometrics.
  - three earlier analysis notebooks.
- **`apps/`**: Google Earth Engine app source (`.js`).
- **`code/`**: pointers to data-preparation code.
- **`media/`**, **`images/`**: site assets.

## Environment setup (uv)

```bash
uv sync                                    # dependencies + the package (editable) + analysis libs incl. expdpy, geometrics
uv run geo4cambodia build [geo|<dataset>]  # regenerate geo/, data/, docs/ from raw/
uv run geo4cambodia validate               # check IDs, schemas, nesting, URLs, CSV = Parquet
uv run geo4cambodia list                   # datasets x scales x years
uv run pytest                              # tests
uv run jupyter lab notebooks/              # open notebooks
uv run jupytext --sync notebooks/*.ipynb   # re-pair after editing a notebook
uv add <package>                           # add a dependency (commit uv.lock)
python3 -m http.server 8000                # preview the website locally
```

- Always use `uv run` for Python and Jupyter.
- After changing anything in `raw/`, `metadata/`, `geo/scales.yaml` or `src/geo4cambodia/build/`, run `build`, `validate` and `pytest`, and commit the regenerated files.
- **Keep the package's own dependencies minimal.** Today they are pandas, numpy, requests, geopandas, pyarrow and pyyaml, all preinstalled in Colab. Optional libraries go in extras (`[raster]` = rasterio); notebook and analysis libraries go in the `analysis` dependency group.
- Version: keep `pyproject.toml` and `__version__` in `src/geo4cambodia/__init__.py` equal. Releases: `docs/publishing.md`.
- Inside the package, import `scales` and `project` as modules (`from . import project`; `from .scales import scales as registry`). The public names `geo.scales()` (a table) and `geo.config()` shadow nothing, but `geo4cambodia.scales` resolves to the function, not the module.
- Commit `uv.lock` after changing dependencies. Never commit `.venv/`.
- The notebooks install packages only when they are missing, so they run unchanged in Colab and locally.

## Spatial scales and geo IDs

Every unit has one **geo ID** (`geo_id`). Administrative IDs follow the GADM 4.1 hierarchy and nest by prefix. Source keys are kept as columns in `geo/units.csv`.

| Scale | Units | geo ID | Source keys kept | Dataset |
| --- | --- | --- | --- | --- |
| `country` | 1 | `KH` | — | — |
| `gdl` (Global Data Lab regions, unions of provinces) | 17 | `KH-GDL-02` | `GDLcode` | `hdi` |
| `province` | 25 | `KH-16` | `gid` (GADM), `shapeISO`, `shapeID` (geoBoundaries), `GDLcode` | `env` |
| `district` | 202 | `KH-16-01` | `gid` (GADM `GID_2`) | `gdppc` |
| `commune`, `grid10k` | planned | `KH-16-01-01`, `KH-G10K-r012c034` | — | — |

- Every unit row carries `<scale>_id` columns for each scale it lies in (`province_id`, `gdl_id`, ...).
- Province numbers follow GADM order and **differ from ISO 3166-2** (Phnom Penh is `KH-16` here, `KH-12` in ISO). `geo.link(..., key="shapeISO")` resolves ISO codes.
- Harmonized province names come from `raw/lookups/province_names.csv`.
- Known data issue: `env.total_NPP` is all zeros in the source release and is published as missing.

## Loading data and building indicators

```python
!pip install -q "geo4cambodia[raster]"             # Google Colab ([raster] for geo.zonal)
import geo4cambodia as geo
geo.datasets(); geo.dictionary("gdppc")             # catalog and variables
df  = geo.load("gdppc")                             # panel: geo_id, year, variables
gdf = geo.load("gdppc", years=2022, geometry=True)  # with boundaries
wide = geo.load("gdppc", wide="trend400_ln_y")      # one column per year
geo.units("district"); geo.boundaries("province"); geo.crosswalk("district", "gdl")
geo.aggregate(geo.load("env"), to="gdl", dataset="env")             # up the hierarchy (metadata rules)
geo.combine(["env", "hdi"], scale="gdl", extra=[my_panel])          # datasets on one scale
geo.overlay(df_2020, grid_gdf, extensive=["pop"], id_col="cell")    # non-nested units, area-weighted
mine = geo.link(table, scale="province", on="Province")             # names/codes -> geo_id
geo.zonal("raster.tif", scale="district", stats=["sum", "mean"], name="ntl", year=2020)
geo.save(panel, "name", scale="province", directory="my_data", variables={...})
gdf, df, df_dict = geo.for_geometrics("gdppc")                      # geometrics: LEVELS ("y") for beta/sigma convergence (logged internally); LOGS ("ln_y") for convergence clubs
df, df_def = geo.for_expdpy("gdppc", groups=["province"])           # for expdpy: analyses variables as given ("ln_y")
```

- **Location of the data.** Outside the repo, the package reads from GitHub: `ref=` or `GEO4CAMBODIA_REF` pins a tag or commit. Inside the repo it reads local files.
- **Without the package**, use the raw URLs, e.g. `https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/data/district/gdppc.csv`.
- **Documentation must always show both ways** of loading: with the package and with plain URLs.

## Updating the website

All content is data in the `CONTENT_REGISTRY` array in `index.html`. To add an item:

1. Add an object with these fields, copying an existing entry of the same type for the type-specific fields:
   - `id`, `type` (`indicator` | `package` | `notebook` | `app` | `insight` | `event`), `section` (`indicators` | `tools` | `insights` | `events`)
   - `title`, `summary`, `description`, `tags`
   - `image`, `imageAlt`
   - `date`, `pinned`
2. Put images in `images/<section>/` as WebP, at most 1600 px wide.
3. The item automatically gets a card and a shareable detail page at `#/<section>/<id>`.
4. Type-specific fields:
   - **New indicator:** first add the data (see `CONTRIBUTING_DATA.md`). Then set `dataset`, `folder` (`data/<scale>`), `docs`, `key: 'geo_id'` and `idExample`. Add `code` with the tabs `python` (package) and `pandas` (plain URL). Add a `Dataset` entry to the JSON-LD block in `<head>`.
   - **Package:** `scope` (the pip command), `install`, `quickstart` (code tabs), optionally `build`, `features` (`{title, fns, text}`) and `links` (kinds `colab`, `docs`, `pypi`, `github`).

**Every code box assumes Google Colab.**
- Each Python snippet on the website (indicator tabs, package quickstarts, the build example) starts with a runnable `!pip install -q <what it needs>`. The same goes for code blocks in README and docs.
- Install `geo4cambodia` (plus `expdpy` or `geometrics` when used). Add `mapclassify` when a snippet maps with `scheme=`, and use `"geo4cambodia[raster]"` when it calls `geo.zonal()`.
- Plain-URL snippets that only use pandas or geopandas need no install line, since Colab has them.
- There are no R or Stata examples.
- Maintainer commands (`uv ...`, releasing) stay as terminal commands.
- Every Python code box links to a blank notebook, `https://colab.research.google.com/notebooks/empty.ipynb`. On the website it is an "Open in Colab" button in the box's footer bar (`CodeBlock`'s `colab` prop; `CodeTabs` sets it). In README and docs (including generated dataset docs) it is the Colab badge below each Python block. Not for BibTeX or terminal commands.

Design tokens are defined in `tailwind.config`: `navy-950…500`, `brand-red` (#d23c3c), `brand-sky` (#7cc4ff). Packages use teal accents. Keep text contrast at WCAG AA or better, keep `prefers-reduced-motion` working, and give every image meaningful `alt` text.

## Preferred libraries

pandas, geopandas, libpysal, esda, splot, mapclassify, mgwr, inequality, statsmodels, matplotlib, seaborn, plotly, **expdpy** (https://cmg777.github.io/expdpy/) for panel exploration and econometrics (FE/RE, Hausman, clustered SEs), and **geometrics** (https://quarcs-lab.github.io/geometrics/) for convergence, spatial dependence and inequality analysis.
