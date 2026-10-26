# Human development, income, night-time lights and population (17 provinces, 2013–2019)

## Overview

This module holds an annual panel of **17 subnational regions of Cambodia, 2013–2019**. It combines the Global Data Lab's subnational Human Development Index (HDI), gross national income (GNI) and population with harmonized DMSP-like night-time lights (NTL). The 17 regions follow the Global Data Lab (GDL) geography. Some regions group several present-day provinces; for example, `KHMr113` is Battambang plus Pailin.

- **Geography:** 17 GDL regions (provinces or groups of provinces)
- **Period:** 2013–2019, annual
- **Categories:** Economy, Health, Social
- **Rows:** 119 (long panel) / 17 (wide panel)

## Files

| File | Form | Description |
| --- | --- | --- |
| `df_cambodia17_20132019_longPanel_HDI_GNI_NTL_POP.csv` | long | One row per region-year |
| `df_cambodia17_20132019_longPanel_HDI_GNI_NTL_POP.dta` | long | Stata version, with variable labels |
| `df_cambodia17_20132019_widePanel_HDI_GNI_NTL_POP.csv` | wide | One row per region, one column per variable-year (e.g. `HDI2019`) |
| `df_cambodia17_20132019_widePanel_HDI_GNI_NTL_POP.dta` | wide | Stata version |
| [`../maps/provinces17_wide.geojson`](../maps/provinces17_wide.geojson) | wide | Wide panel with region polygons (CRS84) |
| [`../maps/provinces17.geojson`](../maps/provinces17.geojson) | — | Region boundaries only (`GDLcode`, `region`) |

## Variable Dictionary

| Variable | Description | Source |
| --- | --- | --- |
| **id** | Region ID (1–17) | — |
| **GDLcode** | Global Data Lab region code (e.g. `KHMr101`) | Smits & Permanyer (2019) |
| **region** | Region name | Smits & Permanyer (2019) |
| **year** | Year | — |
| **NTL** | Night-time lights: sum of DMSP-like digital numbers | Li et al. (2020) |
| **GNI** | Gross national income (thousands of 2011 PPP USD) | Smits & Permanyer (2019) |
| **GNIpc** | Gross national income per capita (2011 PPP USD) | Smits & Permanyer (2019) |
| **HDI** | Subnational Human Development Index (0–1) | Smits & Permanyer (2019) |
| **POP** | Population (thousands) | Smits & Permanyer (2019) |
| **lnNTL** | Log of night-time lights | Derived |
| **lnGNI** | Log of GNI | Derived |
| **lnGNIpc** | Log of GNI per capita (rescaled as in the source panel; recompute from `GNIpc` if you need plain log-dollars) | Derived |
| **lnNTLpc** | Log of night-time lights per capita (rescaled as in the source panel) | Derived |

## Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import pandas as pd
import geopandas as gpd

base = "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/"

# Long panel: one row per region-year
df = pd.read_csv(base + "provinces17-hdi/df_cambodia17_20132019_longPanel_HDI_GNI_NTL_POP.csv")

# Wide panel with polygons: map HDI in 2019
gdf = gpd.read_file(base + "maps/provinces17_wide.geojson")
gdf.plot(column="HDI2019", cmap="viridis", legend=True)
```

```stata
use "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/provinces17-hdi/df_cambodia17_20132019_longPanel_HDI_GNI_NTL_POP.dta", clear
xtset id year
xtsum HDI GNIpc NTL
```

## Related notebooks

- [Monitoring subnational human development in Cambodia](../notebooks/hdi_ntl_esda.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/hdi_ntl_esda.ipynb)

## Data Sources

- Smits, J., & Permanyer, I. (2019). The Subnational Human Development Database. *Scientific Data*, 6, 190038. [https://doi.org/10.1038/sdata.2019.38](https://doi.org/10.1038/sdata.2019.38)
- Li, X., Zhou, Y., Zhao, M., & Zhao, X. (2020). A harmonized global nighttime light dataset 1992–2018. *Scientific Data*, 7, 168. [https://doi.org/10.1038/s41597-020-0510-y](https://doi.org/10.1038/s41597-020-0510-y)

## Recommended Citation

> GeoDevelopment Observatory of Cambodia (2025). *Human development, income, (DMSP-like) lights and population in Cambodia (17 provinces, 2013–2019)*. GeoDevelopment Observatory of Cambodia. https://github.com/quarcs-lab/geo4cambodia/tree/main/provinces17-hdi

## Join Key

Use `GDLcode` (or `id`) to join this module with the boundaries in `../maps/provinces17.geojson` and with `../regionNames/provinces17.csv`. The 17 GDL regions **do not** match the 25 present-day provinces in `provinces25-env`.
