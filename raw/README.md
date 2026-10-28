# raw: original inputs

These files are the untouched originals behind every published file. Never edit them. `uv run geo4cambodia build` regenerates `geo/`, `data/`, `docs/datasets/` and `definitions_gdo-cambodia.csv` from them, and any correction belongs in a builder in `src/geo4cambodia/build/`.

| Path | Source | Used by |
| --- | --- | --- |
| `gdppc/cambodia202-1990-2022-GDPpc.dta` | District GDP per capita, from Kummu et al. (2025) ([original repository](https://github.com/gdo-cambodia/cambodia202-1990-2022-GDPpc)) | `build/gdppc.py` |
| `env/provinces25-1990-2023-pop-viirs-like-egdp-npp-pm25.dta` | Province zonal sums of five remote-sensing products ([original repository](https://github.com/gdo-cambodia/provinces25-1990-2023-pop-viirs-like-egdp-npp-pm25)) | `build/env.py` |
| `hdi/df_cambodia17_20132019_longPanel_HDI_GNI_NTL_POP.dta` | Global Data Lab HDI, GNI and population + DMSP-like lights | `build/hdi.py` |
| `boundaries/districts202_gadm.geojson` | The 202 GADM 4.1 level-2 districts (`GID_2`) | `build/geo.py` |
| `boundaries/provinces17_gdl.geojson` | Global Data Lab region polygons, for reference (GDO dissolves GDL regions from GADM districts instead) | — |
| `lookups/districts202_gadm.csv` | District and province names as spelled in the source | `build/geo.py` |
| `lookups/provinces25_geoboundaries.csv` | geoBoundaries ADM1 keys (`shapeISO`, `shapeID`) | `build/geo.py` |
| `lookups/provinces17_gdl.csv` | Global Data Lab region codes and names | `build/geo.py` |
| `lookups/province_names.csv` | **Hand-checked** links between GADM provinces, geoBoundaries provinces and GDL regions, with harmonized English names | `build/geo.py` (verified against every other source) |
