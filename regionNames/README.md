# Region names and identifiers

## Overview

Lookup tables that map identifiers to names for each geography used in the observatory. Unlike a single-key repository, GDO-Cambodia works with **three geographies**, each with its own key.

## Files

| File | Rows | Key | Columns |
| --- | --- | --- | --- |
| `provinces17.csv` | 17 | `GDLcode` | `id, GDLcode, region` (Global Data Lab regions, some grouping several provinces) |
| `provinces25.csv` | 25 | `shapeISO` | `shapeISO, shapeName, shapeID` (present-day provinces, geoBoundaries ADM1) |
| `districts202.csv` | 202 | `GID_2` | `id, GID_2, province, district` (districts, GADM level 2) |

## Which key goes with which module?

| Module | Geography | Join key |
| --- | --- | --- |
| [`provinces17-hdi`](../provinces17-hdi/) | 17 GDL regions | `GDLcode` / `id` |
| [`provinces25-env`](../provinces25-env/) | 25 provinces | `shapeISO` / `shapeID` |
| [`districts202-gdppc`](../districts202-gdppc/) | 202 districts | `GID_2` / `id` |

> Province spellings differ across sources (e.g. *Banteay Mean Chey*, *Bantey Meanchey*, *BântéayMéanchey*). Harmonize names before matching across geographies.
