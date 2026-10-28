---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: Python 3
  name: python3
---

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_explore.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# Exploring Cambodia's subnational panels with `geo4cambodia` + `expdpy`

Part of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/).

Two packages, one workflow:

- **[geo4cambodia](https://github.com/quarcs-lab/geo4cambodia)** loads the observatory's panels (one row per unit and year) with unit names, the provinces or regions they belong to, and labelled variables.
- **[expdpy](https://cmg777.github.io/expdpy/)** explores panel data: structure, descriptive tables, within/between variation, trajectories, distributions, transitions, missing values and correlations. Every result has a figure or table and a plain-language reading (`.interpret()`).

We explore three panels at three spatial scales:

| Panel | Scale | Years | Section |
| --- | --- | --- | --- |
| `gdppc`: GDP per capita | 202 districts | 1990–2022 | 1 |
| `env`: population, lights, electricity-based GDP, PM2.5 | 25 provinces | 1990–2023 | 2 |
| `hdi`: human development, income, lights | 17 Global Data Lab regions | 2013–2019 | 3 |

The companion notebook [`expdpy_analyze.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_analyze.ipynb) runs panel econometrics on the same data.

+++

## 0. Setup

```{code-cell}
import importlib.util

missing = [p for p in ("geo4cambodia", "expdpy") if importlib.util.find_spec(p) is None]
if missing:
    !pip install -q {" ".join(missing)}
```

```{code-cell}
import warnings

import numpy as np
import geo4cambodia as geo
import expdpy as ex

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*showing .* of")   # expdpy notes when it samples units for readability
```

`geo.for_expdpy()` returns the two inputs expdpy expects: the panel `df` and its data dictionary `df_def` (labels, units and the role of each column), built from the observatory's metadata. `groups=["province"]` adds the name of the province each district lies in. `ex.set_labels(..., set_panel=True)` then declares `geo_id` × `year` as the panel, so later calls need no `entity=` or `time=`.

```{code-cell}
df, df_def = geo.for_expdpy("gdppc", groups=["province"])
df = ex.set_labels(df, df_def, set_panel=True)
df_def
```

## 1. Districts: GDP per capita, 1990–2022

### Structure and summary

```{code-cell}
structure = ex.explore_panel_structure(df)
print(structure.interpret())
structure.fig
```

```{code-cell}
ex.explore_descriptive_table(df[["y", "ln_y"]]).gt
```

### Within and between variation

Do districts differ mostly from *each other* (between), or does each district change mostly *over time* (within)? The answer tells you how much fixed-effects models can learn from the data.

```{code-cell}
xt = ex.explore_xtsum_table(df, var=["y", "ln_y"])
print(xt.interpret())
xt.gt
```

### Trajectories

One line per district, and the quantiles of the distribution over time:

```{code-cell}
ex.explore_spaghetti_plot(df, "ln_y").fig
```

```{code-cell}
ex.explore_quantile_trend_plot(df, var="y").fig
```

Average paths of four contrasting provinces: the capital, the tourism hub around Angkor, the north-western rice bowl, and the remote north-east.

```{code-cell}
four = df[df["province"].isin(["Phnom Penh", "Siem Reap", "Battambang", "Ratanakiri"])]
ex.explore_trend_plot_by_group(four, group_var="province", var="ln_y").fig
```

### Distribution dynamics

How the whole distribution moved, and how often districts change quintile from one year to the next:

```{code-cell}
dist = ex.explore_distribution_over_time(df, "ln_y")
print(dist.interpret())
dist.fig
```

```{code-cell}
trans = ex.explore_transition_matrix(df, "y")
print(trans.interpret())
trans.fig
```

## 2. Provinces: lights, population, electricity-based GDP and PM2.5

The `env` variables are **zonal sums** over 1 km grid cells. We derive comparable per-person and average indicators in pandas:

- `lights_pc`: VIIRS-like lights per 1,000 people
- `egdp_pc`: electricity-based GDP per person
- `pm25`: approximate mean PM2.5 concentration, the zonal sum divided by the number of 0.01° (≈ 1.2 km²) cells in the province

The unit table supplies each province's area; `groups=["gdl"]` adds its Global Data Lab region.

```{code-cell}
env, env_def = geo.for_expdpy("env", groups=["gdl"])
provinces = geo.boundaries("province").merge(geo.units("province")[["geo_id", "area_km2"]], on="geo_id")
lat = provinces.to_crs("EPSG:32648").centroid.to_crs("EPSG:4326").y
cell_km2 = (111.32 * 0.01) ** 2 * np.cos(np.radians(lat))
cells = dict(zip(provinces["geo_id"], provinces["area_km2"].astype(float) / cell_km2))

env["lights_pc"] = env["total_VNL"] / env["total_GlobPOP_Count"] * 1000
env["egdp_pc"] = env["total_EGDP"] / env["total_GlobPOP_Count"]
env["pm25"] = env["total_GHAP"] / env["geo_id"].map(cells)

labels = {"lights_pc": "Night-time lights per 1,000 people", "egdp_pc": "Electricity-based GDP per person",
          "pm25": "Mean PM2.5 (µg/m³, approx.)"}
env, env_def = geo.for_expdpy(env, labels=labels)   # your own panel: published variables keep their labels
env = ex.set_labels(env, env_def, set_panel=True)
```

Each source covers different years, so the panel has many gaps. They are not errors:

```{code-cell}
miss = ex.explore_missing_values_plot(env.drop(columns=["shapeISO", "total_NPP"]))
print(miss.interpret())
miss.fig
```

```{code-cell}
cols = ["lights_pc", "egdp_pc", "pm25", "total_GlobPOP_Count"]
corr = ex.explore_correlation_table(env[cols])
print(corr.interpret())
corr.gt
```

**Within vs between.** Is the association between lights and electricity-based GDP per person the same across provinces (between) as within a province over time (within)? Decomposing it shows why pooled regressions can mislead:

```{code-cell}
wb = ex.explore_scatter_plot_within_between(env.dropna(subset=["lights_pc", "egdp_pc"]), x="lights_pc", y="egdp_pc")
print(wb.interpret())
wb.fig
```

## 3. Global Data Lab regions: human development, 2013–2019

```{code-cell}
hdi, hdi_def = geo.for_expdpy("hdi")
hdi = ex.set_labels(hdi, hdi_def, set_panel=True)

trend = ex.explore_trend_plot(hdi, var=["HDI"])
print(trend.interpret())
trend.fig
```

```{code-cell}
ex.explore_bar_plot_by_group(hdi[hdi["year"] == 2019], by_var="name", var="HDI", order_by_stat=True).fig
```

Which region-years stand out?

```{code-cell}
ex.explore_ext_obs_table(hdi, var="HDI").gt
```

## Next steps

- **Panel econometrics** on these data (fixed vs random effects, Hausman tests, clustered standard errors, convergence): [`expdpy_analyze.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_analyze.ipynb)
- **Spatial analysis** with geometrics: [`geometrics_convergence.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb)
- Explore your own indicator: build it with `geo.link()`, `geo.zonal()` or `geo.combine()` ([quickstart](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb)), then `geo.for_expdpy(my_panel, labels={...})`.
- No code at all: expdpy's [Explore app](https://expdpy-explore.streamlit.app) accepts any CSV, including the observatory's files.
