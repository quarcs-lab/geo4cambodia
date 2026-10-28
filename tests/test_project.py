"""Project-specific tests: facts about Cambodia's units and datasets.

Generic behaviour is tested in tests/test_core.py. A new project built from
this template replaces this file with facts about its own data.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest

import geo4cambodia as geo


# --- scales and units -----------------------------------------------------------------

def test_ancestors_follow_the_hierarchy():
    assert geo.ancestors("district") == ["province", "country", "gdl"]
    assert geo.ancestors("province") == ["country", "gdl"]
    assert geo.ancestors("gdl") == ["country"]
    assert geo.ancestors("country") == []


def test_scale_of_recognises_every_id_pattern():
    assert geo.scale_of("KH") == "country"
    assert geo.scale_of("KH-16") == "province"
    assert geo.scale_of("KH-16-01") == "district"
    assert geo.scale_of("KH-16-01-01") == "commune"
    assert geo.scale_of("KH-GDL-02") == "gdl"
    assert geo.scale_of("KH-G10K-r012c034") == "grid10k"


def test_units_are_unique_and_nest_by_prefix():
    u = geo.units()
    assert u["geo_id"].is_unique
    assert u["scale"].value_counts().to_dict() == {"district": 202, "province": 25, "gdl": 17, "country": 1}
    d = geo.units("district")
    assert (d["geo_id"].str[:5] == d["parent_id"]).all()
    assert d["gid"].is_unique


def test_province_source_keys_are_linked():
    p = geo.units("province").set_index("geo_id")
    assert p.loc["KH-16", "name"] == "Phnom Penh"
    assert p.loc["KH-16", "shapeISO"] == "KH-12"         # ISO numbering differs from GADM order
    assert p.loc["KH-25", "gdl_id"] == "KH-GDL-02"       # Tbong Khmum is in GDL Kampong Cham
    assert p["shapeISO"].is_unique and p["shapeISO"].notna().all()


def test_crosswalk_province_to_gdl_covers_and_sums_to_one():
    xw = geo.crosswalk("province", "gdl")
    assert len(xw) == 25 and xw["geo_id_to"].nunique() == 17
    assert np.allclose(xw.groupby("geo_id_from")["weight_area"].sum(), 1)


# --- loading ----------------------------------------------------------------------------

def test_load_long_wide_and_geometry():
    df = geo.load("gdppc")
    assert list(df.columns[:2]) == ["geo_id", "year"] and len(df) == 202 * 33
    wide = geo.load("gdppc", wide="y")
    assert wide.shape == (202, 34) and "y2022" in wide
    one = geo.load("hdi", years=2019, geometry=True)
    assert isinstance(one, gpd.GeoDataFrame) and len(one) == 17 and one.geometry.notna().all()
    window = geo.load("env", years=(2000, 2005), variables=["total_VNL"])
    assert list(window.columns) == ["geo_id", "year", "total_VNL"] and set(window["year"]) == set(range(2000, 2006))


def test_published_values_match_the_raw_files(tmp_path):
    raw = pd.read_stata("raw/gdppc/cambodia202-1990-2022-GDPpc.dta")
    row = raw[(raw["GID_2"] == "KHM.16.1_2") & (raw["year"] == 2022)].iloc[0]
    got = geo.load("gdppc", years=2022).merge(geo.units("district")[["geo_id", "gid"]], on="geo_id")
    assert got.loc[got["gid"] == "KHM.16.1_2", "y"].item() == pytest.approx(row["y"])
    env = geo.load("env")
    assert env["total_NPP"].isna().all()                  # all-zero source column published as missing


# --- aggregation ----------------------------------------------------------------------

def test_sum_up_the_hierarchy_preserves_totals():
    env = geo.load("env", years=2020, variables=["total_GlobPOP_Count"])
    by_gdl = geo.aggregate(env, to="gdl", dataset="env")
    country = geo.aggregate(env, to="country", dataset="env")
    total = env["total_GlobPOP_Count"].sum()
    assert by_gdl["total_GlobPOP_Count"].sum() == pytest.approx(total)
    assert country["total_GlobPOP_Count"].item() == pytest.approx(total)
    assert by_gdl.set_index("geo_id").loc["KH-GDL-13", "n_units"] == 2   # Battambang + Pailin


def test_weighted_mean_uses_the_weight():
    hdi = geo.load("hdi", years=2019)
    nat = geo.aggregate(hdi, to="country", dataset="hdi", variables=["HDI", "POP"])
    expected = (hdi["HDI"] * hdi["POP"]).sum() / hdi["POP"].sum()
    assert nat["HDI"].item() == pytest.approx(expected)


def test_aggregation_refuses_without_a_rule():
    df = geo.load("gdppc", years=2022)
    with pytest.raises(ValueError, match="No aggregation rule"):
        geo.aggregate(df, to="province", dataset="gdppc", variables=["y"])
    out = geo.aggregate(df, to="province", rules={"y": "mean"}, variables=["y"])
    assert len(out) == 25


def test_aggregation_rejects_non_nested_targets():
    df = geo.load("hdi", years=2019)
    with pytest.raises(ValueError, match="do not nest"):
        geo.aggregate(df, to="province", dataset="hdi")


# --- building your own data ------------------------------------------------------------

def test_link_handles_source_spellings_and_codes():
    mine = pd.DataFrame({"prov": ["BântéayMéanchey", "Phnom Penh", "tbong-khmum"], "v": [1, 2, 3]})
    linked = geo.link(mine, scale="province", on="prov")
    assert linked["geo_id"].tolist() == ["KH-01", "KH-16", "KH-25"]
    with pytest.raises(ValueError, match="pass key"):        # KH-12 is a geo_id and an ISO code
        geo.link(pd.DataFrame({"code": ["KH-12"]}), scale="province", on="code")
    iso = geo.link(pd.DataFrame({"code": ["KH-12"]}), scale="province", on="code", key="shapeISO")
    assert iso["geo_id"].item() == "KH-16"                # ISO code -> GADM-order geo ID
    with pytest.raises(ValueError, match="did you mean 'Kampot'"):
        geo.link(pd.DataFrame({"p": ["Kampott"]}), scale="province", on="p", key="name")


def test_combine_brings_province_and_gdl_data_together():
    both = geo.combine(["env", "hdi"], scale="gdl", years=2019)
    assert len(both) == 17 and {"total_GlobPOP_Count", "HDI"} <= set(both.columns)
    assert "shapeISO" not in both                         # source keys are not variables
    assert both["total_GlobPOP_Count"].sum() == pytest.approx(
        geo.load("env", years=2019)["total_GlobPOP_Count"].sum())
