"""Global Data Lab HDI, GNI, population and DMSP-like lights: raw/hdi -> data/gdl/hdi."""

import pandas as pd

from .. import store
from .common import ids_from_units, publish, tidy_floats, write_docs

DATASET, SCALE = "hdi", "gdl"
RAW = "raw/hdi/df_cambodia17_20132019_longPanel_HDI_GNI_NTL_POP.dta"


def build() -> None:
    df = tidy_floats(pd.read_stata(store.repo_root() / RAW))
    df["geo_id"] = df["GDLcode"].map(ids_from_units(SCALE, "GDLcode"))
    publish(DATASET, SCALE, df)
    write_docs(DATASET)
