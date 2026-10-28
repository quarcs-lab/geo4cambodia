"""Province remote-sensing totals: raw/env -> data/province/env."""

import numpy as np
import pandas as pd

from .. import store
from .common import ids_from_units, publish, tidy_floats, write_docs

DATASET, SCALE = "env", "province"
RAW = "raw/env/provinces25-1990-2023-pop-viirs-like-egdp-npp-pm25.dta"


def build() -> None:
    df = tidy_floats(pd.read_stata(store.repo_root() / RAW))
    df["geo_id"] = df["shapeISO"].map(ids_from_units(SCALE, "shapeISO"))
    # Known issue in the source release: NPP is 0 everywhere, so treat it as missing
    if (df["total_NPP"].fillna(0) == 0).all():
        df["total_NPP"] = np.nan
    # The source has rows for 1986-1989 with no data in any variable: leave those years out
    values = [c for c in df.columns if c.startswith("total_")]
    has_data = df.groupby("year")[values].transform(lambda s: s.notna().any()).any(axis=1)
    df = df[has_data]
    publish(DATASET, SCALE, df)
    write_docs(DATASET)
