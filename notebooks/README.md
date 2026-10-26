# Notebooks

Computational notebooks of the GeoDevelopment Observatory of Cambodia. Every notebook runs in Google Colab (no installation needed) and is paired with a MyST markdown file (`.md`) through [jupytext](https://jupytext.readthedocs.io/) for readable diffs.

| Notebook | Description | Data | Colab |
| --- | --- | --- | --- |
| [`hdi_ntl_esda.ipynb`](hdi_ntl_esda.ipynb) | Monitoring subnational human development: exploratory spatial analysis of HDI, income and night-time lights | Subnational HDI (Global Data Lab), DMSP-like lights | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/hdi_ntl_esda.ipynb) |
| [`districts202_gdppc_eda.ipynb`](districts202_gdppc_eda.ipynb) | Exploratory data analysis of district-level GDP per capita, 1990–2022 | [`districts202-gdppc`](../districts202-gdppc/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_eda.ipynb) |
| [`districts202_gdppc_esda.ipynb`](districts202_gdppc_esda.ipynb) | Exploratory spatial data analysis (spatial autocorrelation, LISA clusters) of trend GDP per capita | [`districts202-gdppc`](../districts202-gdppc/), [`maps`](../maps/) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_esda.ipynb) |

External notebook (not stored here): [Getting remote sensing data in Python](https://colab.research.google.com/drive/1VQFcaKJl0Lz_c_gGrb4FZ2uJvAVseEKp?usp=sharing).

## Running locally

```bash
uv sync                                   # create the environment
uv run jupyter lab                        # open notebooks
uv run jupytext --sync notebooks/*.ipynb  # keep .ipynb and .md in sync after editing
```
