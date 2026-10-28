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

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_analyze.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# Panel econometrics for Cambodia with `geo4cambodia` + `expdpy`

Part of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/).

**[geo4cambodia](https://github.com/quarcs-lab/geo4cambodia)** prepares the panels; **[expdpy](https://cmg777.github.io/expdpy/)** estimates panel models: pooled, between, fixed and random effects, Hausman tests, two-way fixed effects with clustered standard errors, and convergence. Every result reads itself out with `.interpret()`.

Four questions, four sections:

| | Question | Panel |
| --- | --- | --- |
| 1 | Do night-time lights track economic activity? | 25 provinces, 2000–2019; 17 GDL regions, 2013–2019 |
| 2 | What goes with human development? | 17 GDL regions, 2013–2019 |
| 3 | Are districts converging, and does space matter? | 202 districts, 1990–2022 (with geometrics) |
| 4 | Is pollution higher where development is higher? | 25 provinces, 2017–2022 |

The results are **associations**, not causal effects. The exploratory companion is [`expdpy_explore.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_explore.ipynb).

+++

## 0. Setup

```{code-cell}
import importlib.util

missing = [p for p in ("geo4cambodia", "expdpy", "geometrics") if importlib.util.find_spec(p) is None]
if missing:
    !pip install -q {" ".join(missing)}
```

```{code-cell}
import warnings

import numpy as np
import pandas as pd
import geo4cambodia as geo
import expdpy as ex

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="Numba not installed")   # harmless: mapclassify falls back to pure Python
```

## 1. Do night-time lights track economic activity?

Night-time lights are widely used as a proxy for economic activity where GDP statistics are scarce. We relate them to income twice:

- **Provinces, 2000–2019:** electricity-based GDP and VIIRS-like lights. Caveat: the electricity-based GDP series is itself *built* from calibrated night-time lights (Chen et al., 2022), so this is partly a consistency check between two satellite products.
- **GDL regions, 2013–2019:** gross national income from Global Data Lab, which comes from surveys and national accounts, and DMSP-like lights. This is the more independent test.

Some rural provinces show **zero lights** in the 2000s, so we use the inverse hyperbolic sine `asinh(lights)`, which behaves like a log for large values and is defined at zero.

```{code-cell}
env, env_def = geo.for_expdpy("env", years=(2000, 2019))
p = env.dropna(subset=["total_EGDP", "total_VNL"]).copy()
p["ln_egdp"] = np.log(p["total_EGDP"])
p["asinh_lights"] = np.arcsinh(p["total_VNL"])
p["ln_pop"] = np.log(p["total_GlobPOP_Count"])
p, p_def = geo.for_expdpy(p[["geo_id", "year", "ln_egdp", "asinh_lights", "ln_pop"]],
                          labels={"ln_egdp": "Log electricity-based GDP", "asinh_lights": "asinh(night-time lights)",
                                  "ln_pop": "Log population"})
p = ex.set_labels(p, p_def, set_panel=True)
```

`analyze_panel_table` fits four estimators side by side. **Pooled** OLS uses all variation; **between** uses only differences in province averages; **fixed effects** (FE) only changes within each province over time; **random effects** (RE) a weighted mix.

```{code-cell}
models = ex.analyze_panel_table(p, "ln_egdp", ["asinh_lights", "ln_pop"])
print(models.interpret())
models.etable
```

The **Hausman test** asks whether FE and RE estimates differ systematically. If they do, RE's assumption (province effects uncorrelated with the regressors) fails and FE is preferred.

```{code-cell}
print(ex.analyze_hausman_test(p, "ln_egdp", ["asinh_lights", "ln_pop"]).interpret())
```

**Two-way fixed effects** add year effects, which absorb shocks common to all provinces (national growth, sensor changes), with standard errors clustered by province:

```{code-cell}
twfe = ex.analyze_regression_table(p, dvs="ln_egdp", idvs=["asinh_lights", "ln_pop"],
                                   feffects=["geo_id", "year"], clusters=["geo_id"])
print(twfe.interpret())
twfe.etable
```

```{code-cell}
ex.analyze_coefficient_plot(twfe).fig
```

**Reading the results.** Within a province, brighter years go with higher electricity-based GDP (FE coefficient ≈ 0.12, highly significant), and the Hausman test does not reject random effects. Once **year effects** absorb what all provinces share, the lights coefficient falls to almost zero. The within-province association is mostly a common national trend: lights and GDP both grew everywhere. Province-specific deviations from that trend are not matched. This is a typical lesson of two-way fixed effects.

**The independent test: income and lights across GDL regions.** Global Data Lab's GNI does not come from satellites:

```{code-cell}
gdl, gdl_def = geo.for_expdpy("hdi")
gdl = ex.set_labels(gdl, gdl_def, set_panel=True)
income = ex.analyze_panel_table(gdl, "lnGNI", ["lnNTL"])
print(income.interpret())
income.etable
```

**Reading the results.** Across regions (pooled and between), lights say almost nothing about income levels (R² ≈ 0). Within a region over time, income and lights rise together (FE ≈ 0.13). With seven years and no year effects, this again mixes regional dynamics with national growth. For ranking Cambodian regions by income, DMSP-like lights are a weak proxy. A caution on the within estimate: the harmonized lights series switches from DMSP to simulated-VIIRS data around 2013–2014 (total lights more than triple from 2013 to 2014), so part of the within-region change in `lnNTL` is a sensor break rather than growth. Year effects, or starting in 2014, would remove it.

+++

## 2. What goes with human development?

Across Cambodia's 17 GDL regions, is the Human Development Index higher where lights per person are brighter? Here we also bring in province data: `geo.combine()` sums the provinces' population to GDL regions, using the aggregation rules in the metadata.

```{code-cell}
hd = geo.combine({"hdi": None, "env": ["total_GlobPOP_Count"]}, scale="gdl", years=(2013, 2019))
hd["ln_pop"] = np.log(hd["total_GlobPOP_Count"])
hd, hd_def = geo.for_expdpy(hd[["geo_id", "year", "HDI", "lnNTLpc", "ln_pop"]],
                            labels={"ln_pop": "Log population (gridded, summed from provinces)"})
hd = ex.set_labels(hd, hd_def, set_panel=True)

hdi_models = ex.analyze_panel_table(hd, "HDI", ["lnNTLpc", "ln_pop"])
print(hdi_models.interpret())
hdi_models.etable
```

```{code-cell}
print(ex.analyze_hausman_test(hd, "HDI", ["lnNTLpc", "ln_pop"]).interpret())
```

**Reading the results.** Across regions (pooled, between), neither lights per person nor population is associated with HDI. Within regions over time, HDI rises with both (FE: lights per person ≈ 0.008, population ≈ 0.10). The Hausman test **rejects** random effects, because the region effects are correlated with the regressors, so fixed effects are the appropriate estimator. With seven years, these within-region associations largely capture the joint upward trends of 2013–2019.

+++

## 3. Are districts converging, and does space matter?

**β-convergence** asks whether districts that were poorer in 1990 grew faster; **σ-convergence** whether the spread of log incomes narrowed. expdpy estimates both without space. We then compare with [geometrics](https://quarcs-lab.github.io/geometrics/), which models spatial spillovers between neighbouring districts.

```{code-cell}
dist, dist_def = geo.for_expdpy("gdppc", groups=["province"])
dist = ex.set_labels(dist, dist_def, set_panel=True)

beta = ex.analyze_beta_convergence(dist, "ln_y", rolling=False)
print(beta.interpret())
beta.fig
```

```{code-cell}
sigma = ex.analyze_sigma_convergence(dist, "ln_y")
print(sigma.interpret())
sigma.fig
```

```{code-cell}
clubs = ex.analyze_convergence_clubs(dist, "ln_y")
print(clubs.interpret())
clubs.fig
```

**Non-spatial vs spatial.** geometrics needs boundaries and spatial weights, which `geo.for_geometrics()` provides. Note the convention: geometrics takes **levels** (`"y"`) and logs them itself, while expdpy takes the variable you want analysed, here already in logs (`"ln_y"`). Done this way, both estimate the same OLS β.

```{code-cell}
import geometrics as gm

gdf, gdist, gdist_dict = geo.for_geometrics("gdppc")
gdist = gm.set_labels(gdist, gdist_dict, set_panel=True)
w = gm.make_weights(gdf, method="queen")

ols = gm.analyze_beta_convergence(gdist, "y")
sdm = gm.analyze_beta_convergence(gdist, "y", gdf=gdf, w=w, model="sdm")

comparison = pd.DataFrame({
    "model": ["expdpy: OLS (non-spatial)", "geometrics: OLS (non-spatial)", "geometrics: spatial Durbin, total effect"],
    "beta": [beta.beta, ols.beta_total, sdm.beta_total],
    "half-life (years)": [beta.half_life, ols.half_life, sdm.half_life],
}).round(4)
comparison
```

```{code-cell}
print(sdm.interpret())
```

**When does space matter? Here, a lot.** Both packages agree on the non-spatial β (−0.0097, a half-life of about 60 years). Once neighbours enter the model, the total effect in the spatial Durbin model shrinks to about −0.002 and is no longer statistically significant. Income in Cambodia is strongly clustered: Moran's I of log GDP per capita is about 0.6. Much of the apparent catch-up therefore reflects **regional** dynamics, whole neighbourhoods of districts growing together, rather than each poor district closing its own gap. A convergence speed estimated without space would overstate how fast individual districts catch up.

+++

## 4. Is pollution higher where development is higher?

Fine particulate matter (PM2.5) data cover 2017–2022. As in the explore notebook, the mean concentration is approximated as the zonal sum over the number of 0.01° grid cells in each province. Development is measured by lights per person. We fit a quadratic, the shape of an *environmental Kuznets curve*: pollution rising with development and then falling. The first model uses year effects only, so it compares provinces. The second adds province fixed effects, so it uses only changes within provinces.

```{code-cell}
env_all, _ = geo.for_expdpy("env", years=(2017, 2022))
provinces = geo.boundaries("province").merge(geo.units("province")[["geo_id", "area_km2"]], on="geo_id")
lat = provinces.to_crs("EPSG:32648").centroid.to_crs("EPSG:4326").y
cells = dict(zip(provinces["geo_id"], provinces["area_km2"].astype(float) / ((111.32 * 0.01) ** 2 * np.cos(np.radians(lat)))))

q = env_all.dropna(subset=["total_GHAP", "total_VNL"]).copy()
q["pm25"] = q["total_GHAP"] / q["geo_id"].map(cells)
q["ln_lights_pc"] = np.log(q["total_VNL"] / q["total_GlobPOP_Count"] * 1000)
q["ln_lights_pc_sq"] = q["ln_lights_pc"] ** 2
q, q_def = geo.for_expdpy(q[["geo_id", "year", "pm25", "ln_lights_pc", "ln_lights_pc_sq"]],
                          labels={"pm25": "Mean PM2.5 (µg/m³, approx.)", "ln_lights_pc": "Log lights per 1,000 people",
                                  "ln_lights_pc_sq": "Log lights per 1,000 people, squared"})
q = ex.set_labels(q, q_def, set_panel=True)

across = ex.analyze_regression_table(q, dvs="pm25", idvs=["ln_lights_pc", "ln_lights_pc_sq"],
                                     feffects=["year"], clusters=["geo_id"])
print(across.interpret())
across.etable
```

```{code-cell}
within = ex.analyze_regression_table(q, dvs="pm25", idvs=["ln_lights_pc", "ln_lights_pc_sq"],
                                     feffects=["geo_id", "year"], clusters=["geo_id"])
print(within.interpret())
within.etable
```

```{code-cell}
# Where the fitted curve peaks (or bottoms out): -b1 / (2 * b2), in log lights per 1,000 people
coef = across.tidy().set_index("term")["Estimate"]
turning = -coef["ln_lights_pc"] / (2 * coef["ln_lights_pc_sq"])
shape = "peaks" if coef["ln_lights_pc_sq"] < 0 else "bottoms out"
print(f"Across provinces the fitted curve {shape} at {np.exp(turning):.1f} lights per 1,000 people "
      f"(observed range {np.exp(q['ln_lights_pc'].min()):.1f}–{np.exp(q['ln_lights_pc'].max()):.1f}).")
```

**Reading the results.** Neither specification finds a statistically significant association between PM2.5 and lights per person. Across provinces the point estimates even trace a U-shape, the opposite of an environmental Kuznets curve. In these data PM2.5 rather follows population (r ≈ 0.64 in the explore notebook) and regional haze. With 25 provinces and six years, the estimates are fragile. Treat them as a starting point, for example for district-level PM2.5 built with `geo.zonal()`.

+++

## 5. Learn the concepts

expdpy explains every method in plain language:

```{code-cell}
ex.explain("hausman")
```

Other topics: `ex.list_topics()`. Interactive sandboxes such as `ex.learn_pooled_vs_fixed_effects()` simulate data from a known truth.

+++

## Next steps

- Explore the panels first: [`expdpy_explore.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_explore.ipynb)
- Spatial analysis with geometrics: [`geometrics_convergence.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb)
- Bring your own indicators (`geo.link`, `geo.zonal`, `geo.combine`): [quickstart](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb)
- No code: expdpy's [Analyze app](https://expdpy-analyze.streamlit.app)
