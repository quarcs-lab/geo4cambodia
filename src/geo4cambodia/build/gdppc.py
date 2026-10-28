"""District GDP per capita (Kummu et al. 2025): raw/gdppc -> data/district/gdppc."""

import pandas as pd

from .. import store
from .common import ids_from_units, publish, tidy_floats, write_docs

DATASET, SCALE = "gdppc", "district"
RAW = "raw/gdppc/cambodia202-1990-2022-GDPpc.dta"


def build() -> None:
    df = tidy_floats(pd.read_stata(store.repo_root() / RAW))
    df["geo_id"] = df["GID_2"].map(ids_from_units(SCALE, "gid"))
    publish(DATASET, SCALE, df)
    write_docs(DATASET)
