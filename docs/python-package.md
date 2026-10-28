# geo4cambodia

**Subnational development data for Cambodia, ready to analyse, at every spatial scale.**

`geo4cambodia` is the Python package of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/). It loads the observatory's indicators (district GDP per capita, province population, night-time lights, PM2.5, Global Data Lab HDI...) as tidy panels, with boundaries for every scale. It also lets you **build your own indicators**: link your tables to the same unit IDs, summarise rasters over units, move data across scales and combine datasets. It works out of the box in Google Colab.

```python
!pip install geo4cambodia -q            # in Colab; `pip install geo4cambodia` elsewhere

import geo4cambodia as geo

geo.datasets()                                       # what is available, at which scale and years
gdf = geo.load("gdppc", years=2022, geometry=True)   # 202 districts, with boundaries
gdf.plot(column="y", scheme="quantiles", k=5, legend=True)
```

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
import pandas as pd
import geo4cambodia as geo

mine = pd.read_csv("schools_by_province.csv")             # e.g. columns Province, year, schools
mine = geo.link(mine, scale="province", on="Province")     # "BântéayMéanchey" -> KH-01
panel = geo.combine(["env"], scale="province", extra=[mine])
panel["schools_per_10k"] = panel["schools"] / panel["total_GlobPOP_Count"] * 1e4
geo.save(panel, "schools", scale="province", directory="my_data")
```

From a raster:

```python
lights = geo.zonal("viirs_2020.tif", scale="district", stats=["sum", "mean"], name="ntl", year=2020)
```

Then explore and model the panel with expdpy:

```python
import expdpy as ex
df, df_def = geo.for_expdpy("hdi")
df = ex.set_labels(df, df_def, set_panel=True)
ex.analyze_panel_table(df, "HDI", ["lnNTLpc"])            # pooled, between, fixed and random effects
```

Or analyse it spatially with geometrics:

```python
import geometrics as gm
gdf, df, df_dict = geo.for_geometrics("gdppc")
df = gm.set_labels(df, df_dict, set_panel=True)
gm.analyze_beta_convergence(df, "y", gdf=gdf, w=gm.make_weights(gdf)).interpret()   # levels: logged internally
```

## Without the package

Every file is also a plain URL, for R, Stata, Excel or pandas alone:

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/data/district/gdppc.csv")
```

## Installation

```bash
pip install geo4cambodia                    # core: pandas, geopandas, pyarrow, requests, pyyaml
pip install "geo4cambodia[raster]"          # + rasterio, for zonal()
pip install git+https://github.com/quarcs-lab/geo4cambodia   # development version
```

Python 3.11 or later. The data are not inside the package. It reads them from the [GitHub repository](https://github.com/quarcs-lab/geo4cambodia), so installation is quick and you always get the files the website links to. For reproducible research, pin a release of the data with `geo.load(..., ref="v0.3.0")` or the environment variable `GEO4CAMBODIA_REF=v0.3.0`.

## Documentation

- [How the data infrastructure works](https://github.com/quarcs-lab/geo4cambodia/blob/main/docs/data-infrastructure.md): scales, IDs, metadata, aggregation rules, and recipes for building indicators
- [Dataset pages](https://github.com/quarcs-lab/geo4cambodia/tree/main/docs/datasets): variable dictionaries, coverage, sources and citations
- [Website](https://quarcs-lab.github.io/geo4cambodia/): indicators, notebooks, web apps and insights

## Citation

Mendez, C., Khoun, T., & Poortinga, A. (2026). *GeoDevelopment Observatory of Cambodia*. https://quarcs-lab.github.io/geo4cambodia/

MIT License. Original data sources are credited on each dataset page.
