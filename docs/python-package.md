# geo4cambodia

**Subnational development data for Cambodia, ready to analyse, at every spatial scale.**

`geo4cambodia` is the Python package of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/). It loads the observatory's indicators (district GDP per capita, province population, night-time lights, PM2.5, Global Data Lab HDI...) as tidy panels, with boundaries for every scale. It also lets you **build your own indicators**: link your tables to the same unit IDs, summarise rasters over units, move data across scales and combine datasets. It works out of the box in Google Colab: every example below runs in a new Colab notebook (replace the placeholder files, such as your own table or raster, with yours).

```python
!pip install -q geo4cambodia mapclassify           # mapclassify: for scheme="quantiles"
import geo4cambodia as geo

geo.datasets()                                       # what is available, at which scale and years
gdf = geo.load("gdppc", years=2022, geometry=True)   # 202 districts, with boundaries
gdf.plot(column="y", scheme="quantiles", k=5, legend=True)
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

## What it does

| Task | Functions |
| --- | --- |
| **Load** panels (one row per unit and year), names and boundaries | `datasets`, `dictionary`, `load`, `units`, `boundaries`, `crosswalk` |
| **Link** your own tables by unit names or codes, whatever the spelling | `link`, `check` |
| **Extract** indicators from rasters (Earth Engine exports, WorldPop, ...) | `zonal` |
| **Move** data up the hierarchy or onto grids and custom zones | `aggregate`, `overlay`, `overlay_weights` |
| **Combine** datasets at one scale and **save** new ones in the same format | `combine`, `save` |
| **Analyse** with [expdpy](https://cmg777.github.io/expdpy/) (panel exploration, fixed and random effects) and [geometrics](https://quarcs-lab.github.io/geometrics/) (convergence, spatial dependence, inequality) | `for_expdpy`, `for_geometrics` |

## One ID for every unit, at every scale

Every unit has a **geo ID** that nests by prefix (GADM 4.1 hierarchy): district `KH-16-01` lies in province `KH-16` (Phnom Penh), which lies in Cambodia `KH`. Global Data Lab regions (`KH-GDL-02`) are unions of whole provinces. Each dataset is a long panel keyed by `geo_id` and `year`.

| Scale | Units | Example |
| --- | --- | --- |
| `country` | 1 | `KH` |
| `province` | 25 | `KH-16` |
| `district` | 202 | `KH-16-01` |
| `gdl` (Global Data Lab regions) | 17 | `KH-GDL-02` |

## Build your own indicator in five lines

```python
!pip install -q geo4cambodia
import pandas as pd
import geo4cambodia as geo

mine = pd.read_csv("schools_by_province.csv")             # e.g. columns Province, year, schools
mine = geo.link(mine, scale="province", on="Province")     # "BântéayMéanchey" -> KH-01
panel = geo.combine(["env"], scale="province", extra=[mine])
panel["schools_per_10k"] = panel["schools"] / panel["total_GlobPOP_Count"] * 1e4
geo.save(panel, "schools", scale="province", directory="my_data")
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

From a raster:

```python
!pip install -q "geo4cambodia[raster]"            # [raster] adds rasterio
import geo4cambodia as geo

lights = geo.zonal("viirs_2020.tif", scale="district", stats=["sum", "mean"], name="ntl", year=2020)
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

Then explore and model the panel with expdpy:

```python
!pip install -q geo4cambodia expdpy
import geo4cambodia as geo
import expdpy as ex

df, df_def = geo.for_expdpy("hdi")
df = ex.set_labels(df, df_def, set_panel=True)
ex.analyze_panel_table(df, "HDI", ["lnNTLpc"])            # pooled, between, fixed and random effects
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

Or analyse it spatially with geometrics:

```python
!pip install -q geo4cambodia geometrics
import geo4cambodia as geo
import geometrics as gm

gdf, df, df_dict = geo.for_geometrics("gdppc")
df = gm.set_labels(df, df_dict, set_panel=True)
gm.analyze_beta_convergence(df, "y", gdf=gdf, w=gm.make_weights(gdf)).interpret()   # levels: logged internally
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

## Without the package

Every file is also a plain URL, readable with pandas alone (preinstalled in Colab, so nothing to install):

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/data/district/gdppc.csv")
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

## Installation

In a Google Colab cell:

```python
!pip install -q geo4cambodia                    # core: pandas, numpy, geopandas, pyarrow, requests, pyyaml (Colab has them)
!pip install -q "geo4cambodia[raster]"          # + rasterio, for zonal()
!pip install -q git+https://github.com/quarcs-lab/geo4cambodia   # development version
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

Python 3.11 or later. The data are not inside the package. It reads them from the [GitHub repository](https://github.com/quarcs-lab/geo4cambodia), so installation is quick and you always get the files the website links to. For reproducible research, pin a release of the data with `geo.load(..., ref="v0.3.0")` or the environment variable `GEO4CAMBODIA_REF=v0.3.0`.

## Documentation

- [How the data infrastructure works](https://github.com/quarcs-lab/geo4cambodia/blob/main/docs/data-infrastructure.md): scales, IDs, metadata, aggregation rules, and recipes for building indicators
- [Dataset pages](https://github.com/quarcs-lab/geo4cambodia/tree/main/docs/datasets): variable dictionaries, coverage, sources and citations
- [Website](https://quarcs-lab.github.io/geo4cambodia/): indicators, notebooks, web apps and insights

## Citation

Mendez, C., Khoun, T., & Poortinga, A. (2026). *GeoDevelopment Observatory of Cambodia*. https://quarcs-lab.github.io/geo4cambodia/

MIT License. Original data sources are credited on each dataset page.
