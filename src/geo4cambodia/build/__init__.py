"""Builders that regenerate every published file from ``raw/``.

``geo`` must run first: dataset builders take their geo IDs from geo/units.
"""

from . import env, gdppc, geo, hdi
from .common import write_catalog

DATASETS = {"gdppc": gdppc.build, "env": env.build, "hdi": hdi.build}


def build(target: str = "all") -> None:
    if target in ("all", "geo"):
        print("geo")
        geo.build()
    for name, builder in DATASETS.items():
        if target in ("all", name):
            print(name)
            builder()
    if target not in ("all", "geo", *DATASETS):
        raise SystemExit(f"Unknown build target {target!r}; use all, geo or one of {', '.join(DATASETS)}")
    print("catalog")
    write_catalog()
