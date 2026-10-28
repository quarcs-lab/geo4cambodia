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
    publish(DATASET, SCALE, df)
    write_docs(DATASET)
