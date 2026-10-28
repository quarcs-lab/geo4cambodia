# Maps (boundary and panel GeoJSON files)

All files are GeoJSON in geographic coordinates (CRS84 / WGS 84).

| File | Features | Properties | Use |
| --- | --- | --- | --- |
| `provinces17.geojson` | 17 | `GDLcode, region` | Boundaries of the 17 Global Data Lab regions |
| `provinces17_wide.geojson` | 17 | `GDLcode, region, id`, `HDI2013`…`lnNTLpc2019` | Wide panel of [`provinces17-hdi`](../provinces17-hdi/) with polygons |
| `districts202.geojson` | 202 | `GID_2` | Boundaries of the 202 districts |
| `districts202_wide_y.geojson` | 202 | `GID_2, id, province, district, y1990…y2022` | GDP per capita with polygons |
| `districts202_wide_ln_y.geojson` | 202 | `… ln_y1990…ln_y2022` | Log GDP per capita with polygons |
| `districts202_wide_trend400_ln_y.geojson` | 202 | `… trend400_ln_y1990…` | HP trend (λ = 400) with polygons |
| `cambodia-outline.geojson` | 1 | `name` | National outline (districts dissolved, simplified, islands < 0.005 deg² dropped); used by the website's hero globe |

```python
import geopandas as gpd
gdf = gpd.read_file("https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/maps/districts202.geojson")
```

**Known geometry issue:** a few polygons from the upstream sources have nested shells: 5 districts (e.g. `KHM.4.8_2` Tonlé Sap) and 1 GDL region. Mapping and spatial weights work as they are. If a tool needs strictly valid geometries (overlay, dissolve, area), repair them first:

```python
from shapely.validation import make_valid
gdf["geometry"] = gdf.geometry.apply(make_valid)
```

**Disclaimer:** these boundaries are for geo-statistical use only. They are a referential, informational representation of the indicators and do not represent an official definition of Cambodia's territorial boundaries.

Sources: Global Data Lab (17 regions); GADM via Kummu et al. (2025) (202 districts).
