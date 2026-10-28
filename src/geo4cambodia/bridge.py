"""Hand data to companion packages.

`geometrics <https://quarcs-lab.github.io/geometrics/>`_ analyses regional growth,
convergence and inequality with spatial methods. It takes three inputs: ``gdf``
(geometries keyed by an entity id), ``df`` (a long panel) and ``df_dict`` (a data
dictionary). ``for_geometrics`` returns exactly these for any dataset or your own panel::

    import geo4cambodia as geo
    import geometrics as gm

    gdf, df, df_dict = geo.for_geometrics("gdppc")
    df = gm.set_labels(df, df_dict, set_panel=True)
    w = gm.make_weights(gdf, method="queen")
    gm.analyze_beta_convergence(df, "ln_y", gdf=gdf, w=w)
"""

from __future__ import annotations

import pandas as pd

from . import io, metadata
from .scales import scale_of


def for_geometrics(data, scale: str | None = None, years=None, variables=None, labels: dict | None = None,
                   ref: str | None = None):
    """``(gdf, df, df_dict)`` in the format geometrics expects.

    Parameters
    ----------
    data : a dataset id (e.g. ``"gdppc"``) or your own panel with ``geo_id`` and ``year``
        (from ``geo.link``, ``geo.combine``, ``geo.zonal``...)
    scale, years, variables : as in ``geo.load`` (for a dataset id)
    labels : ``{variable: description}`` for your own columns (dataset variables are
        described from the metadata)

    Returns
    -------
    gdf : GeoDataFrame with ``geo_id`` and ``geometry`` (EPSG:4326)
    df : the panel with ``geo_id``, ``name``, ``year`` and the variables
    df_dict : one row per ``df`` column with ``var_name``, ``var_def``, ``label``,
        ``type`` (entity / time / factor / numeric), ``role`` and ``can_be_na``
    """
    described = {}
    if isinstance(data, str):
        df = io.load(data, scale=scale, years=years, variables=variables, ref=ref)
        scale = metadata.resource(data, scale)["geo:scale"]
        for f in metadata.fields(data, scale):
            unit = f.get("geo:unit")
            described[f["name"]] = (f.get("description", ""), f"{f.get('description', '')}" + (f" ({unit})" if unit else ""))
    else:
        df = data.drop(columns="geometry", errors="ignore").copy()
        if scale is None:
            found = {scale_of(i) for i in df["geo_id"].dropna().drop_duplicates()}
            if len(found) != 1:
                raise ValueError(f"Rows mix units from several scales: {sorted(found)}")
            scale = found.pop()
    for name, text in (labels or {}).items():
        described[name] = (text, text)

    names = io.units(scale, ref=ref)[["geo_id", "name"]]
    df = df.drop(columns="name", errors="ignore").merge(names, on="geo_id", how="left")
    first = ["geo_id", "name"] + (["year"] if "year" in df.columns else [])
    df = df[first + [c for c in df.columns if c not in first]]
    gdf = io.boundaries(scale, ref=ref)[["geo_id", "geometry"]]
    gdf = gdf[gdf["geo_id"].isin(df["geo_id"])].reset_index(drop=True)

    rows = []
    for col in df.columns:
        if col == "geo_id":
            typ, role, text = "entity", "", ("geo ID", "geo ID")
        elif col == "name":
            typ, role, text = "factor", "entity_name", ("Unit name", "Name")
        elif col == "year":
            typ, role, text = "time", "", ("Year", "Year")
        else:
            typ = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "factor"
            role, text = "", described.get(col, ("", ""))
        rows.append({"var_name": col, "var_def": text[1], "label": text[0] or col, "type": typ, "role": role,
                     "can_be_na": typ not in ("entity", "time")})
    return gdf, df.reset_index(drop=True), pd.DataFrame(rows)
