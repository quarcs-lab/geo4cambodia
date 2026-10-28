---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: Python 3
  name: python3
---

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# Load, link and build Cambodian indicators with `geo4cambodia`

Part of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/).

This notebook is a hands-on tour of the observatory's data:

1. **Load data without the package**: every file is a plain URL
2. **Load data with the package** `geo4cambodia`
3. **Move data across scales**: districts, provinces, Global Data Lab regions and the country
4. **Link your own table** to the observatory's units, whatever the spelling
5. **Build a new indicator from a raster**
6. **Interpolate to a grid**, then **save** your dataset in the observatory's format

The companion notebook [`geometrics_convergence.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb) analyses the same data with the [geometrics](https://quarcs-lab.github.io/geometrics/) package.

+++

## 0. Setup

In Google Colab the next cell installs the package (a few seconds: Colab already has its dependencies). Locally, `uv sync` has installed it already.

```{code-cell}
import importlib.util

if importlib.util.find_spec("geo4cambodia") is None:
    !pip install -q "geo4cambodia[raster]" mapclassify
```

```{code-cell}
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
```

+++

## 1. Load data without the package

Every published file is a plain URL, so pandas, geopandas, R, Stata or Excel can read it directly. Three kinds of files matter:

- **`data/<scale>/<dataset>.csv`**: the indicators, as a panel with one row per unit (`geo_id`) and year
- **`geo/units.csv`**: names, parent units and the original source codes of every unit
- **`geo/boundaries/<scale>.geojson`**: polygons, keyed by the same `geo_id`

```{code-cell}
BASE = "https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/"

gdppc = pd.read_csv(BASE + "data/district/gdppc.csv")          # 202 districts x 33 years
units = pd.read_csv(BASE + "geo/units.csv")                     # 245 units at 4 scales
districts = gpd.read_file(BASE + "geo/boundaries/district.geojson")

gdppc.head()
```

```{code-cell}
# Names come from geo/units.csv; every row also carries the ids of the units it lies in
names = units.loc[units["scale"] == "district", ["geo_id", "name", "province_id"]]
gdppc_2022 = districts.merge(gdppc[gdppc["year"] == 2022], on="geo_id").merge(names.drop(columns="name"), on="geo_id")

ax = gdppc_2022.plot(column="y", cmap="magma", scheme="quantiles", k=5, legend=True,
                     legend_kwds={"title": "GDP per capita 2022\n(PPP 2017 $)", "loc": "lower left"},
                     edgecolor="white", linewidth=0.2, figsize=(8, 7))
ax.set_axis_off()
ax.set_title("Districts of Cambodia: GDP per capita, 2022 (no package needed)");
```

+++

## 2. Load data with the package

The package does the same in one line, and more: it lists the datasets, describes their variables, filters years and variables, reshapes, and attaches boundaries.

```{code-cell}
import geo4cambodia as geo

geo.datasets()
```

```{code-cell}
geo.dictionary("env")      # every variable: description, unit, aggregation rule, source
```

```{code-cell}
gdf = geo.load("gdppc", years=2022, geometry=True)     # a GeoDataFrame, ready to map
ax = gdf.plot(column="ln_y", cmap="viridis", legend=True, figsize=(7, 6))
ax.set_axis_off()
ax.set_title("Log GDP per capita, 2022 (geo.load with geometry=True)");
```

```{code-cell}
# A window of years and a few variables; or one row per unit with one column per year
lights = geo.load("env", years=(2012, 2023), variables=["total_VNL", "total_GlobPOP_Count"])
wide = geo.load("gdppc", wide="y")
lights.head(3), wide.iloc[:3, :6]
```

```{code-cell}
geo.units("province").head(3)     # names, parents, and the codes each source uses (GADM, geoBoundaries, GDL)
```

+++

## 3. Move data across scales

Each scale nests in the coarser ones, and each variable's metadata says how it may be aggregated (`sum` for totals, `weighted_mean:POP` for HDI, `none` for logs and per-capita values without population).

```{code-cell}
geo.scales()          # the registry of scales
```

```{code-cell}
env = geo.load("env", years=2020)
by_gdl = geo.aggregate(env, to="gdl", dataset="env")             # 25 provinces -> 17 GDL regions
national = geo.aggregate(env, to="country", dataset="env")      # -> Cambodia
national[["geo_id", "year", "total_GlobPOP_Count", "total_VNL", "n_units"]]
```

`geo.combine()` loads several datasets at one scale and aggregates the finer ones on the way. Here, province remote-sensing totals meet Global Data Lab's HDI, and give a new indicator, lights per person:

```{code-cell}
panel = geo.combine(["env", "hdi"], scale="gdl", years=(2013, 2019))
panel["lights_per_person"] = panel["total_VNL"] / panel["total_GlobPOP_Count"]

latest = geo.boundaries("gdl").merge(panel[panel["year"] == 2019], on="geo_id")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, col, title in zip(axes, ["HDI", "lights_per_person"], ["Human Development Index", "Night-time lights per person"]):
    latest.plot(column=col, cmap="YlGnBu", legend=True, ax=ax, edgecolor="white", linewidth=0.4)
    ax.set_title(f"{title}, 2019"); ax.set_axis_off()
```

```{code-cell}
latest[["HDI", "lights_per_person"]].corr()
```

+++

## 4. Link your own table

Tables from reports and ministries identify units by name, spelled in many ways. `geo.link()` attaches the observatory's `geo_id`. It ignores accents, case, spaces and punctuation, and tries every name and code column in `geo.units()`.

The values below are **made up** for the demonstration; replace them with your own data.

```{code-cell}
mine = pd.DataFrame({
    "Province": ["BântéayMéanchey", "Battambang", "KAMPONG CHAM", "Phnom Penh", "Siemréab", "Bantey Meanchey"],
    "year":     [2020, 2020, 2020, 2020, 2020, 2021],
    "clinics":  [41, 77, 63, 120, 58, 43],          # illustrative values
})
mine = geo.link(mine, scale="province", on="Province")
mine
```

```{code-cell}
geo.check(mine, scale="province")        # [] = a valid panel: known ids, one row per unit and year
```

A typo stops with a suggestion instead of silently dropping the row:

```{code-cell}
try:
    geo.link(pd.DataFrame({"Province": ["Kampott"]}), scale="province", on="Province", key="name")
except ValueError as err:
    print(err)
```

+++

## 5. Build a new indicator from a raster

`geo.zonal()` summarises any GeoTIFF (for example an export from Google Earth Engine, or a WorldPop population grid) over the units of a scale. As a self-contained example, we compute a raster of **distance to Phnom Penh**, a simple proxy of market access, and average it over districts.

```{code-cell}
import rasterio
from rasterio.transform import from_bounds

x0, y0, x1, y1 = geo.boundaries("country").total_bounds
nx, ny = 800, 600                                            # about 600 m pixels
lon = np.linspace(x0, x1, nx); lat = np.linspace(y1, y0, ny)
LON, LAT = np.meshgrid(lon, lat)
pp_lat, pp_lon = np.radians(11.5564), np.radians(104.9282)     # Phnom Penh
dlat, dlon = np.radians(LAT) - pp_lat, np.radians(LON) - pp_lon
km = 2 * 6371 * np.arcsin(np.sqrt(np.sin(dlat / 2) ** 2 + np.cos(pp_lat) * np.cos(np.radians(LAT)) * np.sin(dlon / 2) ** 2))

with rasterio.open("distance_to_phnom_penh.tif", "w", driver="GTiff", width=nx, height=ny, count=1,
                   dtype="float32", crs="EPSG:4326", transform=from_bounds(x0, y0, x1, y1, nx, ny)) as dst:
    dst.write(km.astype("float32"), 1)

access = geo.zonal("distance_to_phnom_penh.tif", scale="district", stats=["mean", "max"], name="dist_pp_km")
access.head()
```

Is distance to the capital associated with income? Join the new indicator to the GDP panel:

```{code-cell}
d = geo.load("gdppc", years=2022).merge(access, on="geo_id")
ax = d.plot.scatter(x="dist_pp_km_mean", y="ln_y", alpha=0.6, figsize=(6, 4))
ax.set_xlabel("Mean distance to Phnom Penh (km)"); ax.set_ylabel("Log GDP per capita, 2022")
print(f"correlation: {d['dist_pp_km_mean'].corr(d['ln_y']):.2f}")
```

+++

## 6. Interpolate to a grid and save

Grids, watersheds or old boundaries do not nest in the administrative hierarchy. `geo.overlay()` moves data onto them by area weights. Totals (`extensive`) are split by area; rates (`intensive`) are area-weighted means.

```{code-cell}
from shapely.geometry import box

country = geo.boundaries("country").to_crs("EPSG:32648")       # UTM 48N, metres
gx0, gy0, gx1, gy1 = country.total_bounds
cells = [box(x, y, x + 20_000, y + 20_000) for x in np.arange(gx0, gx1, 20_000) for y in np.arange(gy0, gy1, 20_000)]
grid = gpd.GeoDataFrame({"cell": [f"c{i}" for i in range(len(cells))]}, geometry=cells, crs="EPSG:32648")
grid = grid[grid.intersects(country.geometry.iloc[0])].to_crs("EPSG:4326")

pop = geo.load("env", years=2020, variables=["total_GlobPOP_Count"])
on_grid = geo.overlay(pop, grid, extensive=["total_GlobPOP_Count"], id_col="cell")
print(f"provinces: {pop['total_GlobPOP_Count'].sum():,.0f}  grid: {on_grid['total_GlobPOP_Count'].sum():,.0f}")

ax = grid.merge(on_grid.rename(columns={"geo_id": "cell"}), on="cell").plot(
    column="total_GlobPOP_Count", cmap="magma_r", scheme="quantiles", k=6, figsize=(7, 6))
ax.set_axis_off(); ax.set_title("Population 2020 on a 20 km grid (assumes even spread within provinces)");
```

Finally, save your indicator exactly like the published datasets: CSV, Parquet and a Frictionless datapackage describing every variable. It is then easy to share, reload or contribute to the observatory ([CONTRIBUTING_DATA.md](https://github.com/quarcs-lab/geo4cambodia/blob/main/CONTRIBUTING_DATA.md)).

```{code-cell}
access["year"] = 2024
geo.save(access[["geo_id", "year", "dist_pp_km_mean", "dist_pp_km_max"]], "market_access", scale="district",
         directory="my_data", title="Distance to Phnom Penh",
         description="Mean and maximum straight-line distance from each district to Phnom Penh.",
         variables={"dist_pp_km_mean": {"description": "Mean distance to Phnom Penh", "unit": "km", "aggregation": "none"},
                    "dist_pp_km_max": {"description": "Maximum distance to Phnom Penh", "unit": "km", "aggregation": "max"}})
```

+++

## Next steps

- Analyse these data with **geometrics**: [`geometrics_convergence.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb)
- The full guide: [how the data infrastructure works](https://github.com/quarcs-lab/geo4cambodia/blob/main/docs/data-infrastructure.md)
- Every function has help: `help(geo.link)`
