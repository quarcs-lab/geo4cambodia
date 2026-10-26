# Estimated GDP per capita (202 districts, 1990–2022)

## Overview

This module holds annual estimates of **GDP per capita for Cambodia's 202 districts, 1990–2022**. They are aggregated from the downscaled gridded GDP-per-capita (PPP) dataset of Kummu et al. (2025). Alongside the levels, it provides the log of GDP per capita and Hodrick–Prescott trends with three smoothing parameters (λ = 6.25, 100, 400), for studying long-run regional growth and convergence.

- **Geography:** 202 districts (GADM level 2)
- **Period:** 1990–2022, annual
- **Categories:** Economy
- **Rows:** 6,666 (long panel: 202 × 33) / 202 (wide files)

## Files

| File | Form | Description |
| --- | --- | --- |
| `cambodia202-1990-2022-GDPpc.dta` | long | Full long panel with all variables (Stata, labelled) |
| `wide_y.csv` | wide | GDP per capita, `y1990`…`y2022` |
| `wide_ln_y.csv` | wide | Log GDP per capita |
| `wide_trend6_ln_y.csv` | wide | HP trend of log GDP per capita (λ = 6.25) |
| `wide_trend100_ln_y.csv` | wide | HP trend (λ = 100) |
| `wide_trend400_ln_y.csv` | wide | HP trend (λ = 400) |
| [`../maps/districts202.geojson`](../maps/districts202.geojson) | — | District boundaries (`GID_2`, CRS84) |
| [`../maps/districts202_wide_y.geojson`](../maps/districts202_wide_y.geojson) | wide | GDP per capita with polygons |
| [`../maps/districts202_wide_ln_y.geojson`](../maps/districts202_wide_ln_y.geojson) | wide | Log GDP per capita with polygons |
| [`../maps/districts202_wide_trend400_ln_y.geojson`](../maps/districts202_wide_trend400_ln_y.geojson) | wide | HP trend (λ = 400) with polygons |

## Variable Dictionary

| Variable | Description | Source |
| --- | --- | --- |
| **GID_2** | GADM level-2 code, used for geographic merges | Kummu et al. (2025) |
| **id** | District ID (1–202) | Based on Kummu et al. (2025) |
| **year** | Year | Kummu et al. (2025) |
| **province** | Province name | Kummu et al. (2025) |
| **district** | District name | Kummu et al. (2025) |
| **y** | GDP per capita (PPP, constant 2017 international USD) | Kummu et al. (2025) |
| **ln_y** | Log GDP per capita | Based on Kummu et al. (2025) |
| **trend6_ln_y** | HP trend of log GDP per capita (λ = 6.25) | Based on Kummu et al. (2025) |
| **trend100_ln_y** | HP trend of log GDP per capita (λ = 100) | Based on Kummu et al. (2025) |
| **trend400_ln_y** | HP trend of log GDP per capita (λ = 400) | Based on Kummu et al. (2025) |

In the wide files, each variable becomes one column per year, e.g. `y1990` or `trend400_ln_y2022`.

## Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import geopandas as gpd

url = "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/maps/districts202_wide_y.geojson"
gdf = gpd.read_file(url)

# Map GDP per capita in 2022
gdf.plot(column="y2022", cmap="magma", scheme="quantiles", k=5, legend=True)
```

```stata
use "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/districts202-gdppc/cambodia202-1990-2022-GDPpc.dta", clear
describe
xtset id year
xtsum y ln_y
```

## Related notebooks

- [Exploratory data analysis](../notebooks/districts202_gdppc_eda.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_eda.ipynb)
- [Exploratory spatial data analysis](../notebooks/districts202_gdppc_esda.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_esda.ipynb)

## Data Source

- Kummu, M., Kosonen, M., & Masoumzadeh Sayyar, S. (2025). Downscaled gridded global dataset for gross domestic product (GDP) per capita PPP over 1990–2022. *Scientific Data*, 12, 178. [https://doi.org/10.1038/s41597-025-04487-x](https://doi.org/10.1038/s41597-025-04487-x)

## Recommended Citation

> He, D., Mendez, C., & Li, X. (2025). *Estimates of district-level GDP per capita in Cambodia 1990–2022*. GeoDevelopment Observatory of Cambodia. https://github.com/quarcs-lab/geo4cambodia/tree/main/districts202-gdppc

Original repository: [gdo-cambodia/cambodia202-1990-2022-GDPpc](https://github.com/gdo-cambodia/cambodia202-1990-2022-GDPpc)

## Join Key

Use `GID_2` to join with `../maps/districts202.geojson`, or `id` to join with `../regionNames/districts202.csv`.
