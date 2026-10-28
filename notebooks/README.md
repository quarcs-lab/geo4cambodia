# Notebooks

Computational notebooks of the GeoDevelopment Observatory of Cambodia. Every notebook runs in Google Colab (no installation needed) and is paired with a MyST markdown file (`.md`) through [jupytext](https://jupytext.readthedocs.io/) for readable diffs.

| Notebook | Description | Data | Colab |
| --- | --- | --- | --- |
| [`geo4cambodia_quickstart.ipynb`](geo4cambodia_quickstart.ipynb) | Load data with and without the `geo4cambodia` package, move it across scales, link your own table, build an indicator from a raster, interpolate to a grid and save | all datasets | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geo4cambodia_quickstart.ipynb) |
| [`expdpy_explore.ipynb`](expdpy_explore.ipynb) | `geo4cambodia` + [expdpy](https://cmg777.github.io/expdpy/): panel structure, within/between variation, trajectories, transitions, missing values and correlations at three scales | `gdppc`, `env`, `hdi` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_explore.ipynb) |
| [`expdpy_analyze.ipynb`](expdpy_analyze.ipynb) | `geo4cambodia` + expdpy: lights and income, human development, convergence with and without space, pollution and development (FE, RE, Hausman tests) | `env`, `hdi`, `gdppc` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/expdpy_analyze.ipynb) |
| [`geometrics_convergence.ipynb`](geometrics_convergence.ipynb) | `geo4cambodia` + [geometrics](https://quarcs-lab.github.io/geometrics/): LISA clusters, β-, σ- and club convergence, and inequality between and within provinces | [`gdppc`](../docs/datasets/gdppc.md) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/geometrics_convergence.ipynb) |
| [`hdi_ntl_esda.ipynb`](hdi_ntl_esda.ipynb) | Monitoring subnational human development: exploratory spatial analysis of HDI, income and night-time lights | Subnational HDI (Global Data Lab), DMSP-like lights | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/hdi_ntl_esda.ipynb) |
| [`districts202_gdppc_eda.ipynb`](districts202_gdppc_eda.ipynb) | Exploratory data analysis of district-level GDP per capita, 1990–2022 | [`gdppc`](../docs/datasets/gdppc.md) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_eda.ipynb) |
| [`districts202_gdppc_esda.ipynb`](districts202_gdppc_esda.ipynb) | Exploratory spatial data analysis (spatial autocorrelation, LISA clusters) of trend GDP per capita | [`gdppc`](../docs/datasets/gdppc.md), [`geo`](../geo/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_esda.ipynb) |

External notebook (not stored here): [Getting remote sensing data in Python](https://colab.research.google.com/drive/1VQFcaKJl0Lz_c_gGrb4FZ2uJvAVseEKp?usp=sharing).

## Running locally

```bash
uv sync                                   # create the environment (includes geo4cambodia, expdpy and geometrics)
uv run jupyter lab                        # open notebooks
uv run jupytext --sync notebooks/*.ipynb  # keep .ipynb and .md in sync after editing
```

In Colab, every notebook installs what it needs (`geo4cambodia`, `expdpy`, `geometrics`, ...) only if it is missing. The data are read from this repository through the package, or as plain URLs, except in `hdi_ntl_esda`, which reads its original sources.
