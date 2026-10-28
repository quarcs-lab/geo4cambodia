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

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# Are Cambodia's districts converging? Spatial analysis with `geo4cambodia` + `geometrics`

Part of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/).

Two packages, one workflow:

- **[geo4cambodia](https://github.com/quarcs-lab/geo4cambodia)** gets the data ready: the district GDP-per-capita panel (202 districts, 1990–2022), with boundaries, names and variable labels.
- **[geometrics](https://quarcs-lab.github.io/geometrics/)** analyses them: maps, spatial dependence, β- and σ-convergence, convergence clubs and inequality. Every result has a figure (`.fig`), a table (`.df`) and a plain-language reading (`.interpret()`).

Loading and building the data is covered in the companion notebook [`geo4cambodia_quickstart.ipynb`](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb).

+++

## 0. Setup

```{code-cell}
import importlib.util

missing = [p for p in ("geo4cambodia", "geometrics") if importlib.util.find_spec(p) is None]
if missing:
    !pip install -q {" ".join(missing)}
```

```{code-cell}
import warnings
import geo4cambodia as geo
import geometrics as gm

warnings.filterwarnings("ignore", message="Numba not installed")    # harmless: mapclassify falls back to pure Python
```

## 1. From geo4cambodia to geometrics in one line

geometrics takes three inputs: `gdf` (geometries keyed by an entity id), `df` (a long panel) and `df_dict` (a data dictionary with labels and the role of each column). `geo.for_geometrics()` builds all three from any dataset of the observatory, using its metadata for the labels.

```{code-cell}
gdf, df, df_dict = geo.for_geometrics("gdppc")
df = gm.set_labels(df, df_dict, set_panel=True)      # declares geo_id x year as the panel
df_dict
```

```{code-cell}
df.head()
```

Spatial weights define who is a neighbour: here, districts that share a border (queen contiguity).

```{code-cell}
w = gm.make_weights(gdf, method="queen")
gm.explore_connectivity_map(gdf, w=w).fig
```

## 2. Explore: where is income high, and does it cluster?

```{code-cell}
gm.explore_choropleth_map(df, "y", gdf=gdf, period=2022).fig
```

How has the distribution of districts changed? Relative to the national average, in four years:

```{code-cell}
gm.explore_distribution_over_time(df, "y", relative=True, periods=[1990, 2000, 2010, 2022]).fig
```

**Spatial autocorrelation.** Moran's I measures whether rich districts sit next to rich districts:

```{code-cell}
moran = gm.explore_moran_plot(df, "ln_y", gdf=gdf, w=w, period=2022)
print(moran.interpret())
moran.fig
```

```{code-cell}
gm.explore_moran_over_time(df, "ln_y", gdf=gdf, w=w).fig
```

**Local clusters (LISA)** show *where* high-high hot spots and low-low cold spots are:

```{code-cell}
lisa = gm.explore_lisa_cluster_map(df, "ln_y", gdf=gdf, w=w, period=2022)
print(lisa.interpret())
lisa.fig
```

## 3. Analyse: convergence

geometrics' β- and σ-convergence functions take a variable **in levels** (`"y"`, GDP per capita) and work with its logarithm internally. Pass `"y"`, not `"ln_y"`, or the data would be logged twice. Convergence clubs are the exception: they use the variable as supplied, so they take the log (`"ln_y"`).

**β-convergence.** Did poorer districts in 1990 grow faster? First a cross-section OLS, then a spatial Durbin model, which lets growth depend on the neighbours' growth and initial income.

```{code-cell}
beta = gm.analyze_beta_convergence(df, "y")                          # OLS: no weights needed
print(beta.interpret())
beta.fig
```

```{code-cell}
beta_sdm = gm.analyze_beta_convergence(df, "y", gdf=gdf, w=w, model="sdm")
print(beta_sdm.interpret())
```

**σ-convergence.** Is the dispersion of log income across districts shrinking?

```{code-cell}
sigma = gm.analyze_sigma_convergence(df, "y")
print(sigma.interpret())
sigma.fig
```

**Convergence clubs** (Phillips and Sul). If the whole country does not converge to one path, groups of districts may converge to their own paths. This test takes log GDP per capita:

```{code-cell}
clubs = gm.analyze_convergence_clubs(df, "ln_y", gdf=gdf)
print(clubs.interpret())
clubs.fig
```

## 4. Analyse: inequality

```{code-cell}
ineq = gm.analyze_inequality_over_time(df, "y")
print(ineq.interpret())
ineq.fig
```

**Between and within provinces.** The Theil index splits inequality into differences between provinces and differences among the districts of each province. geo4cambodia's unit table already says which province every district lies in:

```{code-cell}
provinces = geo.units("province")[["geo_id", "name"]].rename(columns={"geo_id": "province_id", "name": "province"})
df_prov = df.merge(geo.units("district")[["geo_id", "province_id"]], on="geo_id").merge(provinces, on="province_id")
df_prov = gm.set_labels(df_prov, df_dict, set_panel=True)

theil = gm.analyze_theil_decomposition(df_prov, "y", "province")
print(theil.interpret())
theil.fig
```

## 5. Learn the concepts

geometrics explains every method in plain language:

```{code-cell}
gm.explain("beta_convergence")
```

## 6. Your turn

- Repeat the analysis with a Hodrick–Prescott trend to remove short-run fluctuations. `"trend400_ln_y"` is already in logs: pass it as it is to the clubs test, and as levels (`df["trend400_y"] = np.exp(df["trend400_ln_y"])`) to β- and σ-convergence.
- Analyse another dataset: `geo.for_geometrics("hdi")` (17 GDL regions), or `geo.for_geometrics("env")` (25 provinces) for night-time lights. Some provinces record zero lights in early years, so use years with positive values (zeros end in 2014, so e.g. `years=(2015, 2023)`) before taking logs.
- Analyse **your own indicator**: build a panel with `geo.link()`, `geo.zonal()` or `geo.combine()` (see the [quickstart](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb)), then pass it on with `geo.for_geometrics(my_panel, labels={"my_var": "My indicator"})`.
- Compare spatial weights: `gm.make_weights(gdf, method="knn", k=6)`.
