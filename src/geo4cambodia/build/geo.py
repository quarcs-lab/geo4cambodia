"""Build ``geo/``: units with geo IDs, boundaries and crosswalks for every active scale.

Inputs (in ``raw/``):
- ``boundaries/districts202_gadm.geojson``: the 202 GADM 4.1 level-2 districts (``GID_2``)
- ``lookups/districts202_gadm.csv``: district and province names as in the source
- ``lookups/province_names.csv``: hand-checked links between GADM provinces,
  geoBoundaries ADM1 (``shapeISO``) and Global Data Lab regions (``GDLcode``)
- ``lookups/provinces25_geoboundaries.csv`` and ``lookups/provinces17_gdl.csv``

Provinces, GDL regions and the country are dissolved from the districts, so
every scale nests exactly in the next one.
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd

from .. import project, store
from .common import dissolve, publish_geo, split_camel


def _check(cond: bool, message: str) -> None:
    if not cond:
        raise ValueError(f"raw lookups are inconsistent: {message}")


def build() -> None:
    raw = store.repo_root() / "raw"
    cc = project.country_code()                     # "KH"
    districts = pd.read_csv(raw / "lookups/districts202_gadm.csv")
    provinces = pd.read_csv(raw / "lookups/province_names.csv")
    gb = pd.read_csv(raw / "lookups/provinces25_geoboundaries.csv")
    gdl = pd.read_csv(raw / "lookups/provinces17_gdl.csv")
    shapes = gpd.read_file(raw / "boundaries/districts202_gadm.geojson")

    # --- consistency of the hand-made province table with every source -------------
    parsed = districts["GID_2"].str.extract(r"^KHM\.(\d+)\.(\d+)_2$").astype(int)
    districts["p"], districts["d"] = parsed[0], parsed[1]
    gadm_names = districts.groupby("p")["province"].first()
    _check(sorted(provinces["gadm_index"]) == sorted(gadm_names.index), "GADM province indexes")
    _check((provinces.set_index("gadm_index")["name_gadm"] == gadm_names).all(), "GADM province names")
    _check(set(provinces["shapeISO"]) == set(gb["shapeISO"]), "geoBoundaries shapeISO codes")
    gb_names = gb.set_index("shapeISO")["shapeName"]
    _check((provinces.set_index("shapeISO")["name_geoboundaries"] == gb_names.loc[provinces["shapeISO"]].values).all(),
           "geoBoundaries names")
    _check(set(provinces["GDLcode"]) == set(gdl["GDLcode"]), "GDL codes")
    _check(set(shapes["GID_2"]) == set(districts["GID_2"]), "district boundaries vs lookup")

    # --- units: geo_id, scale, name, parent_id + source keys ----------------------
    gdl = gdl.assign(geo_id=lambda d: f"{cc}-GDL-" + d["GDLcode"].str[-2:])
    provinces = provinces.assign(
        geo_id=lambda d: f"{cc}-" + d["gadm_index"].map("{:02d}".format),
        gdl_id=lambda d: d["GDLcode"].map(dict(zip(gdl["GDLcode"], gdl["geo_id"]))),
        shapeID=lambda d: d["shapeISO"].map(gb.set_index("shapeISO")["shapeID"]),
        gid=lambda d: "KHM." + d["gadm_index"].astype(str) + "_1",
    )
    districts = districts.assign(
        geo_id=lambda d: f"{cc}-" + d["p"].map("{:02d}".format) + "-" + d["d"].map("{:02d}".format),
        name=lambda d: d["district"].map(split_camel),
    )
    districts["parent_id"] = districts["geo_id"].str[:-3]
    units = pd.concat([
        pd.DataFrame([{"geo_id": cc, "scale": "country", "name": project.config()["country"]["name"],
                       "gid": project.config()["country"]["iso3"]}]),
        gdl.assign(scale="gdl", name=gdl["region"], name_gdl=gdl["region"], parent_id=cc),
        provinces.assign(scale="province", parent_id=cc),
        districts.assign(scale="district", gid=districts["GID_2"], name_gadm=districts["district"]),
    ], ignore_index=True)[["geo_id", "scale", "name", "parent_id", "gdl_id",
                           "gid", "shapeISO", "shapeID", "GDLcode", "name_gadm", "name_geoboundaries", "name_gdl"]]

    # --- boundaries: dissolved upwards from the districts, so every scale nests ---
    shapes = shapes.merge(districts[["GID_2", "geo_id", "parent_id"]], on="GID_2")
    shapes["gdl_id"] = shapes["parent_id"].map(provinces.set_index("geo_id")["gdl_id"])
    shapes["country_id"] = cc
    layers = {"district": shapes[["geo_id", "geometry"]],
              "province": dissolve(shapes, "parent_id"),
              "gdl": dissolve(shapes, "gdl_id"),
              "country": dissolve(shapes, "country_id")}
    publish_geo(units, layers)
