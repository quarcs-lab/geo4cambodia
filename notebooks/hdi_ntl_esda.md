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

+++ {"id": "view-in-github", "colab_type": "text"}

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/hdi_ntl_esda.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

+++ {"id": "tPbPpRITIv3z"}


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1MtUkRi8Q27KPC67qJmD-c-lER6-47Jjx?usp=sharing)


# **A geocomputational notebook to monitor the dynamics of regional development**

Carlos Mendez (Nagoya Univerisity)


[![DOI](https://zenodo.org/badge/683583423.svg)](https://zenodo.org/badge/latestdoi/683583423)
```
Suggested citation:
Mendez, C.(2023). A geocomputational notebook to monitor the dynamics of regional development. Zenodo. https://doi.org/10.5281/zenodo.828685
```

+++ {"id": "SqB8rdDFeelR"}

## 0) Motivation

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 421
id: 3-wwGoQ9rZGv
outputId: bba338d9-502e-4870-baa7-7f553b9dc12d
---
# @title Development differences across and within coutries

from IPython.display import YouTubeVideo

YouTubeVideo(id='jbkSRLYSojo', width=600, height=400, autoplay=False, controls=True)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 421
id: kOorqo_Krjck
outputId: f181b0ba-0e36-4a7a-aabb-1f41ef5435ba
---
# @title The human development index

from IPython.display import YouTubeVideo

YouTubeVideo(id='1ScfqaCp2Ho', width=600, height=400, autoplay=False, controls=True)

```

```{code-cell}
---
cellView: form
colab:
  base_uri: https://localhost:8080/
  height: 421
id: CJGzM191qeP_
outputId: ee0459e1-9907-4df4-c794-e720aede0463
---
# @title Studying economic development from outer space

from IPython.display import YouTubeVideo

YouTubeVideo(id='rm1gCLfaZnE', width=600, height=400, autoplay=False, controls=True)
```

+++ {"id": "8_SIXDr4fCu7"}

This compuational notebook uses  estimates from the subnational human development database of
>  [Smits, J., & Permanyer, I. (2019). The subnational human development database. Scientific data, 6(1), 1-15.](https://www.nature.com/articles/sdata201938)

An overview of the dataset can be found here:
- [Short note introducing the dataset](https://hdr.undp.org/en/content/subnational-human-development-index-moving-beyond-country-level-averages)
- [Paper introducing the dataset](https://www.nature.com/articles/sdata201938)

This notebook is based on version 5.0 of the database, which is mantained and distributed by the Global Data Lab of the Radboud University of The Netherlands. The database can be freely downloaded from https://globaldatalab.org/shdi/download_files/.

The notebook also uses satellite nighttime light images from from
> [Li, X., Zhou, Y., Zhao, M. et al. A harmonized global nighttime light dataset 1992–2018. Sci Data 7, 168 (2020)](https://doi.org/10.1038/s41597-020-0510-y)

The repository of images is available at https://doi.org/10.6084/m9.figshare.9828827.v8

+++ {"id": "op7BfWwqIv32"}

## 1) Setup

```{code-cell}
---
id: T4mxke3PJL03
colab:
  base_uri: https://localhost:8080/
outputId: 6d08a5f0-8d9f-4514-8331-4b17948a6100
---
# Adding necessary libraries to Google Colab environment

# Installing the 'contextily' library for adding basemaps to plots
!pip install contextily -q

# Installing the 'splot' library for spatial data visualization
!pip install splot -q

# Installing additional libraries for spatial analysis and visualization
!pip install rasterio -q  # Library for reading and writing raster data
!pip install mapclassify -q  # Library for choropleth mapping
!pip install inequality -q  # Library for measuring economic inequality

# Installing the 'mgwr' library for performing geographically weighted regression
!pip install mgwr -q
```

```{code-cell}
:id: q5IRSgHJ01tI

#!pip install linearmodels==4.27 -q  # Library for linear models and instrumental variables
```

```{code-cell}
:id: hr0ihHLoTfR4

# Importing necessary libraries for data analysis and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable  # Function to create a new axis on a plot

import seaborn as sns
sns.set(style="darkgrid", context="paper", font_scale=1.02)  # Setting seaborn styles

import glob
import os
import requests
import zipfile
from io import BytesIO

import plotly.express as px
import plotly.graph_objects as go

# Importing libraries for spatial data and visualization
import geopandas as gpd
import contextily as cx

import libpysal
from libpysal import weights
from libpysal.weights import Queen

import rasterio  # Library for raster data processing
from rasterio import plot as rioplot  # Function to plot raster data
from rasterio.mask import mask  # Function for masking raster data using shapefile for zonal statistics

# Exploratory Spatial Data Analysis (ESDA) tools
import mapclassify as mc
import esda
from esda.moran import Moran, Moran_Local

# Spatial plotting tools
import splot
from splot.esda import moran_scatterplot, plot_moran, lisa_cluster, plot_local_autocorrelation
from splot.libpysal import plot_spatial_weights
from splot.mapping import vba_choropleth

# Library for inequality analysis
import inequality
from inequality.gini import Gini_Spatial

# Statistical modeling
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Geographically Weighted Regression (GWR) and related utilities
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
from mgwr.utils import shift_colormap, truncate_colormap

# linearmodels library provides helps performing regressions
#from linearmodels import PooledOLS  # Function to perform pooled OLS regression
#from linearmodels import PanelOLS  # Function to perform OLS regression on panel data
#from linearmodels import BetweenOLS  # Function to compute the between estimator of an OLS regression
#from linearmodels.panel.results import compare  # Function to compare results of an OLS regression

# Suppressing warnings for cleaner output
import warnings
warnings.filterwarnings('ignore')
```

+++ {"id": "qHHgLyWOL0GG"}

## 2) Import data and set key variables

+++ {"id": "3BSx0aDI8xg7"}

### 2.1) Import dataframe

```{code-cell}
:id: psv1iQEPxG1H

df = pd.read_csv("https://github.com/quarcs-lab/data-open/raw/master/shdi/SHDIold.csv").sort_values(by=['year', 'SubContinent'])
df["year"]= df["year"].astype(str)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: dB-MNadmxQxy
outputId: 9e8ea793-eb29-4932-d3aa-bdbb1ba7b3f9
---
df.info()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 617
id: UMyELioUxXIt
outputId: 47041aba-666b-4c13-b379-9591a1d30e95
---
df
```

+++ {"id": "SEPjRDhM9FAO"}

### 2.2) Import map

```{code-cell}
:id: vjUJgY9bxW5F

map = gpd.read_file("https://gist.github.com/cmg777/81b6e2b1ea5865c09daf3b2bbf35bbf8/raw/5e0a0370f453421bc503594cfae1e466c89e449f/GDL%2520Shapefiles%2520V4.geojson")
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: DkV2zo_U5t-c
outputId: c865b919-097d-4ad9-d1a7-25cbb921c6ee
---
map.info()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 424
id: 7GCAATqW4gWy
outputId: 38dc6faa-4cc4-46c6-898c-c1db39b5243a
---
map
```

```{code-cell}
---
id: TK4MBapCxWrq
colab:
  base_uri: https://localhost:8080/
  height: 258
outputId: 7c2507c7-8154-4a7a-f872-801e2d89b862
---
map.plot('shdi');
```

+++ {"id": "PfoqweJd49oE"}

### 2.1) Prepare dictionary

```{code-cell}
:id: 4ruMrnEx5D0d

# Prepare dictionary of variables and labels
column_names = ['Variable', 'Label']
data = [
    ['iso_code', 'ISO Code'],
    ['country', 'Country'],
    ['year', 'Year'],
    ['GDLcode', 'GDL Code'],
    ['continent2', 'Continent 2'],
    ['level', 'Level'],
    ['region', 'Region'],
    ['continent', 'Continent'],
    ['CountryName_std', 'Country Name (Standardized)'],
    ['shdi', 'Human Development Index'],
    ['healthindex', 'Health Index'],
    ['incindex', 'Income Index'],
    ['edindex', 'Education Index'],
    ['esch', 'Expected Schooling (Years)'],
    ['msch', 'Mean Schooling (Years)'],
    ['lifexp', 'Life Expectancy'],
    ['gnic', 'Gross National Income per Capita'],
    ['lgnic', 'Logged Gross National Income per Capita'],
    ['pop', 'Population'],
    ['POLY_IDcountry', 'POLY ID (Country)'],
    ['iso3', 'ISO3'],
    ['status', 'Status'],
    ['CountryName', 'Country Name'],
    ['SubContinent', 'Subcontinent'],
    ['Continent', 'Continent'],
    ['Continent_std', 'Continent (Standardized)'],
    ['_merge', 'Merge']
]

dataDefinitions  = pd.DataFrame(data, columns=column_names)
```

```{code-cell}
---
id: Sc23Ld245J71
colab:
  base_uri: https://localhost:8080/
  height: 896
outputId: 526ef569-0d3c-46f2-cfba-df0caa253e44
---
dataDefinitions
```

```{code-cell}
:id: TftW9FrB5Lq0

data_dict = dict(zip(dataDefinitions['Variable'], dataDefinitions['Label']))
```

+++ {"id": "JgE-EaLeIv34"}

### 2.2) Set key variables

```{code-cell}
:id: tlXYe-sn6GDg

COUNTRY = 'Cambodia'
#COUNTRY = 'Indonesia'
#COUNTRY = 'Lao'
#COUNTRY = 'India'
#COUNTRY = 'Bolivia'
#COUNTRY = 'Thailand'
```

```{code-cell}
:id: CO4x_dTA6jaa

FOCUS_YEAR = '2019'
```

```{code-cell}
:id: JWcURAH_Iv36

INDICATOR1 = 'shdi'
```

```{code-cell}
:id: Y_Z6lnBBIv36

INDICATOR2 = 'healthindex'
```

```{code-cell}
:id: m-1Sh5dtIv36

INDICATOR3 = 'incindex'
```

```{code-cell}
:id: OtsxnR7AIv37

INDICATOR4 = 'edindex'
```

```{code-cell}
:id: b5IZHAq_Kli4

INDICATOR5 = 'pop'
```

```{code-cell}
:id: GW0WF72fTgLt

INDICATOR6 = 'lgnic'
```

```{code-cell}
:id: ykyBbpPfLa55

INDICATOR7 = 'gnic'
```

```{code-cell}
:id: iPDRnxkvTF-s

ADM1 = 'region'
```

```{code-cell}
:id: EZbnhtMPTFf2

ADM2 = 'region'
```

```{code-cell}
:id: gFXAEtgTTFSo

ADM3 = 'region'
```

```{code-cell}
:id: HDbjCtKdkc_p

startYear = 2013
```

```{code-cell}
:id: Rx1syQoikd11

endYear   = 2019
```

```{code-cell}
:id: LikeJNNmfuCZ

years = np.arange(startYear, endYear+1).astype(str)
```

+++ {"id": "t1BQBA4s3qYb"}

## 3) Data processing, selection, and fitering




```{code-cell}
:id: WzY_ychS3hG5

# Remove national observations and focus on Cambodia
df1 = df[(df.level != 'National') & (df.country == COUNTRY)]
```

```{code-cell}
:id: qdQhIGrMa3Lj

# Save df1 as csv
df1.to_csv("df1.csv", index = False)
```

```{code-cell}
:id: -hddyaKf2_c9

mapCountry = map[map['country'] == COUNTRY][['GDLcode', 'geometry']]
```

```{code-cell}
:id: ghD1KR883Kw-

gdf = mapCountry.merge(df1[df1['year'] == FOCUS_YEAR], on=['GDLcode'], how='left')
# Save gdf as geojson file
gdf.to_file("gdf_full.geojson", driver="GeoJSON")
```

```{code-cell}
:id: C07WKlOhl7of

# Drop unnecessary columsn
columns_to_drop = ['iso_code', 'country', 'year', 'continent2', 'level', 'continent', 'CountryName_std', 'shdi', 'healthindex', 'incindex', 'edindex', 'esch', 'msch', 'lifexp', 'gnic', 'lgnic', 'pop', 'POLY_IDcountry', 'iso3', 'status', 'CountryName', 'SubContinent','Continent', 'Continent_std', '_merge']
gdf = gdf.drop(columns=columns_to_drop)
# Save gdf as geojson file
gdf.to_file("gdf.geojson", driver="GeoJSON")
```

```{code-cell}
:id: JpykDKtDvfCC

# Select key variable
df1_INDICATOR1 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR1]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR1 = df1_INDICATOR1.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR1).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR1.columns = df1_wide_INDICATOR1.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR1 = mapCountry.merge(df1_wide_INDICATOR1, on=['GDLcode'], how='left')
# Save gdf_INDICATOR1 as geojson file
gdf_INDICATOR1.to_file("gdf_INDICATOR1.geojson", driver="GeoJSON")
```

```{code-cell}
:id: X1rc9mE3CdUG

# Select key variable
df1_INDICATOR2 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR2]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR2 = df1_INDICATOR2.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR2).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR2.columns = df1_wide_INDICATOR2.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR2 = mapCountry.merge(df1_wide_INDICATOR2, on=['GDLcode'], how='left')
# Save gdf_INDICATOR2 as geojson file
gdf_INDICATOR2.to_file("gdf_INDICATOR2.geojson", driver="GeoJSON")
```

```{code-cell}
:id: yQSSMIuJCjYk

# Select key variable
df1_INDICATOR3 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR3]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR3 = df1_INDICATOR3.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR3).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR3.columns = df1_wide_INDICATOR3.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR3 = mapCountry.merge(df1_wide_INDICATOR3, on=['GDLcode'], how='left')
# Save gdf_INDICATOR3 as geojson file
gdf_INDICATOR3.to_file("gdf_INDICATOR3.geojson", driver="GeoJSON")
```

```{code-cell}
:id: 37BcpaXADLc3

# Select key variable
df1_INDICATOR4 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR4]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR4 = df1_INDICATOR4.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR4).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR4.columns = df1_wide_INDICATOR4.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR4 = mapCountry.merge(df1_wide_INDICATOR4, on=['GDLcode'], how='left')
# Save gdf_INDICATOR4 as geojson file
gdf_INDICATOR4.to_file("gdf_INDICATOR4.geojson", driver="GeoJSON")
```

```{code-cell}
:id: cGDeXRGIDLTn

# Select key variable
df1_INDICATOR5 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR5]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR5 = df1_INDICATOR5.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR5).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR5.columns = df1_wide_INDICATOR5.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR5 = mapCountry.merge(df1_wide_INDICATOR5, on=['GDLcode'], how='left')
# Save gdf_INDICATOR5 as geojson file
gdf_INDICATOR5.to_file("gdf_INDICATOR5.geojson", driver="GeoJSON")
```

```{code-cell}
:id: nN8al6aoDLJ3

# Select key variable
df1_INDICATOR6 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR6]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR6 = df1_INDICATOR6.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR6).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR6.columns = df1_wide_INDICATOR6.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR6 = mapCountry.merge(df1_wide_INDICATOR6, on=['GDLcode'], how='left')
# Save gdf_INDICATOR6 as geojson file
gdf_INDICATOR6.to_file("gdf_INDICATOR6.geojson", driver="GeoJSON")
```

```{code-cell}
:id: lULAoCvjDK_Y

# Select key variable
df1_INDICATOR7 = df1.loc[df1['country'] == COUNTRY, ['GDLcode', ADM3, 'year', INDICATOR7]]
# Pivot panel data from long form to wide form
df1_wide_INDICATOR7 = df1_INDICATOR7.pivot_table(
    index=["GDLcode", ADM3],
    columns="year",
    values= INDICATOR7).reset_index(drop=False)
# Make sure the column names are strings
df1_wide_INDICATOR7.columns = df1_wide_INDICATOR7.columns.astype(str)
# Merge with polygonsFile
gdf_INDICATOR7 = mapCountry.merge(df1_wide_INDICATOR7, on=['GDLcode'], how='left')
# Save gdf_INDICATOR7 as geojson file
gdf_INDICATOR7.to_file("gdf_INDICATOR7.geojson", driver="GeoJSON")
```

+++ {"id": "PcWpZ8VINZRu"}

## 4) Exploratory data analysis (EDA)

```{code-cell}
---
id: XnDc2E3nS7en
colab:
  base_uri: https://localhost:8080/
  height: 805
outputId: 77c0c53b-9532-4419-aaeb-e4789c4453f1
---
# Exploring data using the explore() function on the GeoDataFrame
gdf_INDICATOR1.explore(
    column='region',                        # Column to visualize
    tooltip=[ADM1,'2019'],  # Information in tooltip
    categorical=True,                    # Categorical column
    legend=True,                         # Show legend
    tiles='CartoDB positron',            # Basemap style (Other options: CartoDB positron, OpenStreetMap, Stamen Terrain)
    style_kwds=dict(color="gray", weight=0.6),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)     # Customize legend
)
```

+++ {"id": "OoI5bX2NIv37"}

### 4.1) Descriptive statistics

+++ {"id": "yCCfLg_EIv37"}

- What do we know about the centrality and dispersion of our development indicator?

```{code-cell}
---
id: davYPzluIv37
colab:
  base_uri: https://localhost:8080/
  height: 330
outputId: a8cca561-b5b5-4407-e7a7-7562da873774
---
gdf_INDICATOR1.describe().round(2)
```

+++ {"id": "_PPHUHiCIv37"}

### 4.2) Regional development differences

+++ {"id": "8juS6q-BIv37"}

- How is our development indicator disbributed across the 339 municipalities and 9 departments of Bolivia?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: kTSO1Bo6YIjs
outputId: 97ac9809-9b1b-4d56-f57c-c53278edaf12
---
# Creating a strip plot using Plotly Express
px.strip(
    df1,
    x=INDICATOR1,                 # Data for x-axis
    y=ADM1,                      # Data for y-axis
    color=ADM1,                  # Color grouping based on 'dep'
    animation_frame= 'year',
    range_x= [0.20, 0.95],
    hover_name=ADM3,             # Municipality for hover tooltip
    hover_data=[ADM1, INDICATOR1, INDICATOR2, INDICATOR3, INDICATOR4, INDICATOR5, INDICATOR6, INDICATOR7],     # Additional data for hover tooltip
    labels=dict(data_dict)        # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: RiiR51x2YvTo
outputId: d5d8922c-93a6-45fc-b3a8-8dcd746c91d8
---
# Creating a histogram using Plotly Express
px.histogram(
    df1,
    x=INDICATOR1,                    # Data for x-axis
    range_x= [0.20, 0.80],
    animation_frame= 'year',
    color=ADM1,                     # Color grouping based on 'dep'
    hover_name=ADM3,                # Municipality for hover tooltip
    marginal='rug',                  # Display rug plot on the marginal axis
    hover_data=[ADM1, INDICATOR4],        # Additional data for hover tooltip
    labels=dict(data_dict)           # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 7A36wjpJYdvj
outputId: 34e9be10-48fd-4c5f-d496-d8195936fe7a
---
# Creating a box plot using Plotly Express
px.box(
    df1,
    x=INDICATOR1,                 # Data for x-axis
    range_x= [0.20, 0.80],
    #y=ADM1,                      # Data for y-axis
    animation_frame= 'year',
    #color=ADM1,                  # Color grouping based on 'dep'
    hover_name=ADM3,             # Municipality for hover tooltip
    hover_data=[ADM1, INDICATOR4],     # Additional data for hover tooltip
    labels=dict(data_dict)        # Custom labels from data_dict
)
```

+++ {"id": "lB7-mMhMIv38"}

### 4.3) Population and development

+++ {"id": "1Oz5xuoLIv38"}

- Do the most populous regions tend to be more developed?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: cEDK7PJxX_aY
outputId: 833e055e-2921-4e89-976a-1a6f1f441476
---
px.bar(
    df1[df1['year'] == FOCUS_YEAR].sort_values(by=INDICATOR5, ascending=True),
    x=ADM3,                    # Data for x-axis
    y=INDICATOR5,               # Data for y-axis
    log_y=False,                # Disable logarithmic y-axis scale
    hover_data=[INDICATOR1, INDICATOR5],  # Additional data for hover tooltip
    labels=dict(data_dict)         # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: taUqrvaxQ8S6
outputId: a3c9ae46-c744-42be-938d-d111ab46504a
---
px.bar(
    df1[df1['year'] == FOCUS_YEAR].sort_values(by=INDICATOR1, ascending=True),
    x=ADM3,                    # Data for x-axis
    y=INDICATOR1,               # Data for y-axis
    log_y=False,                # Disable logarithmic y-axis scale
    hover_data=[INDICATOR1, INDICATOR5],  # Additional data for hover tooltip
    labels=dict(data_dict)         # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: uwKiNfdOY5bg
outputId: c17a9fc2-c67e-44d8-f24c-5f056972ecd9
---
# Creating a treemap using Plotly Express
px.treemap(
    df1[df1['year'] == FOCUS_YEAR],
    color=INDICATOR1,                # Data for coloring
    values=INDICATOR5,                # Data for size of treemap blocks
    path=[ADM3],             # Path for hierarchical display
    hover_name= ADM3,                # Municipality for hover tooltip
    hover_data=[INDICATOR1],        # Additional data for hover tooltip
    labels=dict(data_dict)           # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: xgY_0neZIv38
outputId: b2a5e47d-8113-4927-d80c-7866d22e5172
---
# Creating a sunburst plot using Plotly Express
px.sunburst(
    df1[df1['year'] == FOCUS_YEAR],
    color=INDICATOR1,                # Data for coloring
    values=INDICATOR5,                # Data for size of sunburst segments
    path=[ADM3],             # Path for hierarchical display
    hover_name=ADM3,                # Municipality for hover tooltip
    hover_data=[INDICATOR5],        # Additional data for hover tooltip
    labels=dict(data_dict)           # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: glN7NntEYMv2
outputId: 0382eb70-8d67-4563-99c4-ea6aaac0e01d
---
px.scatter(
    df1,
    x=INDICATOR5,                             # Data for x-axis
    log_x = False,
    #range_x= [0, 2200],
    range_y= [0.20, 0.95],
    y=INDICATOR1,                             # Data for y-axis
    #color=ADM1,                              # Data for color coding
    #symbol=ADM1,                             # Data for symbol coding
    hover_name=ADM3,                         # Municipality for hover tooltip
    trendline='ols',                          # Adding OLS trendline
    #trendline_scope= "overall",
    hover_data=[INDICATOR1],                 # Additional data for hover tooltip
    #marginal_x= 'box',
    #marginal_y= 'box',
    animation_frame= 'year',
    labels=dict(data_dict)                    # Custom labels from data_dict
)
```

+++ {"id": "z_WQiUi7Iv39"}

### 4.4) Nighttime lights and development (preview)

+++ {"id": "5jHa-XmoIv39"}

- Can nighttime lights help us predict regional development?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 805
id: 3CXPOu0gOoHm
outputId: e67e5c4b-6003-4724-851b-9d8e59cfb45b
---
# Exploring data using the explore() function on the GeoDataFrame
gdf_INDICATOR1.explore(
    column='2019',                 # Column to visualize
    tooltip=[ADM1,'2019'],  # Information to show in tooltip
    k=3,                               # Number of classes for visualization
    scheme='FisherJenks',              # Classification scheme (info: https://pysal.org/mapclassify/generated/mapclassify.FisherJenks.html#mapclassify.FisherJenks)
    cmap='BuPu',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles= cx.providers.NASAGIBS.ViirsEarthAtNight2012,           # Basemap style (other options: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html)
    style_kwds=dict(color="gray", weight=0.4, alpha=0.9),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

+++ {"id": "NFuf8dCvXiO-"}

### 4.5) Time series

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: SHwXVeAoXsAM
outputId: fa671fd0-7f81-470c-a716-42c31463aaff
---
px.line(
    df1,
    x="year",
    y= INDICATOR1,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: rhH4QkzHakPD
outputId: 7fe3d9de-fc07-4ce2-98ef-80dfec0fe5b2
---
px.line(
    df1,
    x="year",
    y= INDICATOR2,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: VOZwNnG7a27E
outputId: 572b6cd1-4df6-4482-e971-a9b9bb3820b0
---
px.line(
    df1,
    x="year",
    y= INDICATOR4,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: F1lY_8iCaryJ
outputId: 61499e61-3aaa-4913-f249-8f7b930affe6
---
px.line(
    df1,
    x="year",
    y= INDICATOR3,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 6uaCqrb1aLLj
outputId: 434fb7ef-c81b-4706-ef4a-5025def5cb9b
---
px.line(
    df1,
    x="year",
    y= INDICATOR6,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: cKT7gkL2cBZc
outputId: 541ce7af-cf4e-4d38-9603-d54d22444bdb
---
px.line(
    df1,
    x="year",
    y= INDICATOR7,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: SRdkiODgZ6NR
outputId: fce6ff5e-94b6-4d55-d55c-71c71ebac1df
---
px.line(
    df1,
    x="year",
    y= INDICATOR5,
    log_y= False,
    color= ADM3,
    #hover_name="country",
    #hover_data= ['country'],
    labels=dict(data_dict)
    )
```

+++ {"id": "kqmQCBqPQgoB"}

## 5) Exploratory spatial data analysis (ESDA)

```{code-cell}
:id: fD7-uCxr0TFo

# Define the URL where the GeoJSON data is located
dataURL = '/content/gdf_INDICATOR1.geojson'

# Read the GeoJSON file from the specified URL using GeoPandas
# The resulting GeoDataFrame is assigned to the variable 'data'
data = gpd.read_file(dataURL)
data = data.to_crs(epsg=4326)
data["id"] = data.index.astype(str)
geojson_dict = data.__geo_interface__
```

```{code-cell}
---
id: sOdEXDGdUgFn
colab:
  base_uri: https://localhost:8080/
  height: 617
outputId: cc03f445-257a-403b-f781-3bc8a2ff5ef8
---
  # Plot with proper geojson and explicit color scale "viridis"
  fig = px.choropleth_mapbox(
      data_frame=data,
      geojson=geojson_dict,
      locations="id",
      color="2019",
      hover_name = 'region',
      hover_data=['2019', '1990'],
      color_continuous_scale="RdBu_r",
      mapbox_style="carto-positron",
      zoom=5.5,
      center={"lat": data.geometry.centroid.y.mean(), "lon": data.geometry.centroid.x.mean()},
      opacity=0.6
  )

  # Set figure dimensions to 600x600 pixels (6 in x 6 in at 100 DPI)
  fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=630, height=600)
  fig.show()
```

```{code-cell}
:id: XGhuU0FY0AxO

fig.write_html("mapINDICATOR1.html", include_plotlyjs='cdn')
```

+++ {"id": "3ASeA2tfIv39"}

### 5.1) Spatial distribution

+++ {"id": "xZ1t4KpYDLWq"}

#### 5.1.1) Box-plot breaks

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: TDtX-JFIEViU
outputId: 2198dcb4-e69b-4bf3-fae2-799ce855709e
---
# Creating a box plot using Plotly Express
px.box(gdf_INDICATOR1,
    x='2019',                 # Data for x-axis
    hover_name='region',             # Municipality for hover tooltip
    hover_data=['1992', '2019'],     # Additional data for hover tooltip
    labels=dict(data_dict)        # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 805
id: eJGYcIzhDKjV
outputId: 9ed67223-6409-4e0f-a984-9ff995d9eb56
---
# Exploring data using the explore() function on the GeoDataFrame
gdf_INDICATOR1.explore(
    column='2019',                 # Column to visualize
    tooltip=['region', '1992', '2019'],  # Information to show in tooltip
    scheme='BoxPlot',              # Classification scheme (info: https://pysal.org/mapclassify/generated/mapclassify.BoxPlot.html#mapclassify.BoxPlot)
    k=6,                            # Number of classes for coloring
    cmap='coolwarm',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles='CartoDB positron',            # Basemap style (other options: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html)
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: _tNG1MrRJppD
outputId: f41ddd0c-722a-433a-81c1-279cff4297cc
---
mc.BoxPlot(gdf_INDICATOR1['2019'])
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 587
id: ug71fbIiKAFr
outputId: 508e0577-e59d-479d-856b-ad71726c4b1b
---
# Create a figure and axis for plotting
fig, ax = plt.subplots(figsize=(9, 6))

# Plot the GeoDataFrame with specified settings
gdf_INDICATOR1.plot(
    column='2019',              # Data for coloring
    scheme='BoxPlot',           # Classification scheme
    cmap='coolwarm',                # Color map for visualization
    edgecolor='k',                  # Color of edges
    linewidth=0.5,                  # Width of edge lines
    alpha=0.8,                      # Transparency
    legend=True,                    # Show legend
    ax=ax,                          # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1.00, 1.10)}  # Legend customization
)

# Adding a basemap using contextily
#cx.add_basemap(
    #ax,                             # Axis to add basemap to
    #crs=gdf.crs.to_string(),         # Coordinate reference system
    #source=cx.providers.Stamen.TonerHybrid,  # Basemap source
    #attribution=False               # Disable attribution
#)

# Set plot title and adjust layout
#plt.title('Spatial distribution: Three natural breaks')
plt.tight_layout()

# Turn off axis display
ax.axis("off")

# Display the plot
plt.show()
```

+++ {"id": "8Im3S0aBC6yP"}

#### 5.1.2) Fisher-Jenks breaks

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 805
id: ProSA9MXZpy5
outputId: b7846950-2e69-4040-fd3f-263a66a31eaf
---
# Exploring data using the explore() function on the GeoDataFrame
gdf_INDICATOR1.explore(
    column='2019',                 # Column to visualize
    tooltip=['region'],  # Information to show in tooltip
    k=3,                               # Number of classes for visualization
    scheme='FisherJenks',              # Classification scheme (info: https://pysal.org/mapclassify/generated/mapclassify.FisherJenks.html#mapclassify.FisherJenks)
    cmap='coolwarm',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles='CartoDB positron',            # Basemap style (other options: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html)
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: qevIRWERJspo
outputId: 699e8bd7-e55a-4440-974d-f561c189dd03
---
mc.FisherJenks(gdf_INDICATOR1['2019'], k=3)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 583
id: mP-LAGS9Iv39
outputId: 8ccda012-aaa3-4acc-9af6-632a773ff9b4
---
# Create a figure and axis for plotting
fig, ax = plt.subplots(figsize=(9, 6))

# Plot the GeoDataFrame with specified settings
gdf_INDICATOR1.plot(
    column='2019',              # Data for coloring
    scheme='FisherJenks',           # Classification scheme
    k=3,                            # Number of classes for coloring
    cmap='coolwarm',                # Color map for visualization
    edgecolor='k',                  # Color of edges
    linewidth=0.5,                  # Width of edge lines
    alpha=0.8,                      # Transparency
    legend=True,                    # Show legend
    ax=ax,                          # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1.00, 0.92)}  # Legend customization
)

# Adding a basemap using contextily
#cx.add_basemap(
    #ax,                             # Axis to add basemap to
    #crs=gdf.crs.to_string(),         # Coordinate reference system
    #source=cx.providers.Stamen.TonerHybrid,  # Basemap source
    #attribution=False               # Disable attribution
#)

# Set plot title and adjust layout
#plt.title('Spatial distribution: Three natural breaks')
plt.tight_layout()

# Turn off axis display
ax.axis("off")

# Display the plot
plt.show()
```

+++ {"id": "ILWNZyUkIv3-"}

### 5.2) Spatial dependence

+++ {"id": "RjIcSBGJIv3-"}

- To what extent is the performance of a region similar to that of its neighbours?
- To what extent is there is an overall pattern of "clustering"?
- Where can we find statistically significant spatial clusters?
- Where can we find statistically significant spatial outliers?

+++ {"id": "-R7WuY9EDUw6"}

#### 5.2.1) Spatial connectivity

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 664
id: Txiy8di4aLhR
outputId: 5d38991c-e1c7-48aa-85ab-338c4de7e9a3
---
# Create K-nearest neighbors spatial weights
W = weights.KNN.from_dataframe(gdf, k=4)

# Transform the weights to row-standardized
W.transform = 'r'

# Plot the spatial weights using splot
plot_spatial_weights(W, gdf);
```

+++ {"id": "_E_xsOEkCXBk"}

#### 5.2.2) Global dependence

```{code-cell}
:id: QcN-RFbL-hV3

def moran_by_col(y, w=W):
    mo = esda.Moran(y, w=w)
    mo_s = pd.Series(
        {"I": mo.I, "I-P value": mo.p_sim},
    )
    return mo_s
```

```{code-cell}
:id: k5191tka_vSo

moran_dynamics_INDICATOR1 = gdf_INDICATOR1[years].apply(moran_by_col, axis=0).T
moran_dynamics_INDICATOR2 = gdf_INDICATOR2[years].apply(moran_by_col, axis=0).T
moran_dynamics_INDICATOR3 = gdf_INDICATOR3[years].apply(moran_by_col, axis=0).T
moran_dynamics_INDICATOR4 = gdf_INDICATOR4[years].apply(moran_by_col, axis=0).T
moran_dynamics_INDICATOR5 = gdf_INDICATOR5[years].apply(moran_by_col, axis=0).T
moran_dynamics_INDICATOR6 = gdf_INDICATOR6[years].apply(moran_by_col, axis=0).T
moran_dynamics_INDICATOR7 = gdf_INDICATOR7[years].apply(moran_by_col, axis=0).T
```

```{code-cell}
:id: 0F7Qamr-D1n4

def plot_moran_dynamics(indicator_data):
    """
    Plot Moran's I and P-value dynamics.

    Parameters:
    - indicator_data: DataFrame or similar structure containing 'I' and 'I-P value' columns.

    Returns:
    None
    """
    # Plot 'I' values
    plt.plot(indicator_data.index, indicator_data['I'], label="Moran's I", linestyle='-')

    # Plot 'I-P value' values
    plt.plot(indicator_data.index, indicator_data['I-P value'], label='P-value', linestyle='--')

    # Adding labels and legend
    plt.xlabel("")
    plt.ylabel("Moran's I and P-value ")
    plt.legend()

    # Adjusting x-axis tick spacing
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    # Display the combined graph
    plt.tight_layout()  # Ensure all elements fit in the figure
    plt.show()

# Example usage: plot_moran_dynamics(moran_dynamics_INDICATOR1)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 487
id: wTv_aC8YD21e
outputId: 95cedc49-fbfe-44fc-85cf-be2e4789a95b
---
plot_moran_dynamics(moran_dynamics_INDICATOR1)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 807
id: NYa3BywIBS72
outputId: 6247af51-4448-4952-ca48-b8221f57e278
---
# Create a 2x2 subplot grid
fig, axs = plt.subplots(2, 2, figsize=(10, 8), sharey=True)  # Added sharey=True

# Set the y-axis limits for all figures
y_axis_limits = (-0.1, 0.5)

# Figure 1
axs[0, 0].plot(moran_dynamics_INDICATOR1.index, moran_dynamics_INDICATOR1['I'], label="Moran's I of HDI index ", linestyle='-')
axs[0, 0].plot(moran_dynamics_INDICATOR1.index, moran_dynamics_INDICATOR1['I-P value'], label='P-value', linestyle='--')
axs[0, 0].set_xlabel("")
axs[0, 0].set_ylabel("Moran's I and P-value: HDI index ")
axs[0, 0].legend()
axs[0, 0].tick_params(axis='x', rotation=45, labelsize=6)
axs[0, 0].set_ylim(y_axis_limits)  # Set y-axis limits

# Figure 2
axs[0, 1].plot(moran_dynamics_INDICATOR2.index, moran_dynamics_INDICATOR2['I'], label="Moran's I of Health index", linestyle='-')
axs[0, 1].plot(moran_dynamics_INDICATOR2.index, moran_dynamics_INDICATOR2['I-P value'], label='P-value', linestyle='--')
axs[0, 1].set_xlabel("")
axs[0, 1].set_ylabel("Moran's I and P-value: Health index  ")
axs[0, 1].legend()
axs[0, 1].tick_params(axis='x', rotation=45, labelsize=6)
axs[0, 1].set_ylim(y_axis_limits)  # Set y-axis limits

# Figure 3
axs[1, 0].plot(moran_dynamics_INDICATOR3.index, moran_dynamics_INDICATOR3['I'], label="Moran's I of Income index", linestyle='-')
axs[1, 0].plot(moran_dynamics_INDICATOR3.index, moran_dynamics_INDICATOR3['I-P value'], label='P-value', linestyle='--')
axs[1, 0].set_xlabel("")
axs[1, 0].set_ylabel("Moran's I and P-value: Income index ")
axs[1, 0].legend()
axs[1, 0].tick_params(axis='x', rotation=45, labelsize=6)
axs[1, 0].set_ylim(y_axis_limits)  # Set y-axis limits

# Figure 4
axs[1, 1].plot(moran_dynamics_INDICATOR4.index, moran_dynamics_INDICATOR4['I'], label="Moran's I of Education index", linestyle='-')
axs[1, 1].plot(moran_dynamics_INDICATOR4.index, moran_dynamics_INDICATOR4['I-P value'], label='P-value', linestyle='--')
axs[1, 1].set_xlabel("")
axs[1, 1].set_ylabel("Moran's I and P-value: Education index ")
axs[1, 1].legend()
axs[1, 1].tick_params(axis='x', rotation=45, labelsize=6)
axs[1, 1].set_ylim(y_axis_limits)  # Set y-axis limits

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
```

+++ {"id": "pP0e8udaCp-L"}

#### 5.2.3) Local dependence

```{code-cell}
:id: Fjtq7tmYLV88

def visualize_spatial_association(gdf_INDICATOR, W, year):
    """
    Visualize spatial association using Moran's I and Local Indicators of Spatial Association (LISA).

    Parameters:
    - gdf_INDICATOR: GeoDataFrame containing the indicator data for the specified year.
    - W: Spatial weights matrix.
    - year: The specific year for which spatial association is visualized.

    Returns:
    None
    """
    # Calculate global Moran's I
    globalMoran_INDICATOR = Moran(gdf_INDICATOR[year], W)
    MoranI_INDICATOR = "{:.2f}".format(globalMoran_INDICATOR.I)

    # Calculate local indicators of spatial association
    localMoran_INDICATOR = Moran_Local(gdf_INDICATOR[year], W, permutations=999, seed=12345)

    # Create subplots for visualizations
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

    # Plotting Moran scatterplot
    moran_scatterplot(localMoran_INDICATOR, p=0.10, aspect_equal=False, zstandard=False, ax=axes[0])

    # Plotting Local Indicators of Spatial Association (LISA) clusters
    lisa_cluster(localMoran_INDICATOR, gdf_INDICATOR, p=0.10, legend_kwds={'bbox_to_anchor': (0.02, 0.90)}, ax=axes[1])

    # Setting labels and titles for the plots
    axes[0].set_xlabel('Indicator')
    axes[0].set_ylabel('Spatial lag of indicator')
    axes[0].set_title(f"(a) Moran scatterplot (Moran's I = {MoranI_INDICATOR})")
    axes[1].set_title("(b) Spatial clusters and outliers (p < 0.10)")

    # Display the plots
    plt.show()

# Example usage: visualize_spatial_association(gdf_INDICATOR1, W, '2019')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 504
id: RXT4j4FVLYi0
outputId: b866bd11-7a7d-4ac2-fd4c-3d753039314e
---
visualize_spatial_association(gdf_INDICATOR1, W, '2019')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 504
id: PrVN2wDELpTf
outputId: 0838c23c-44bf-41c7-8d21-b5124d2034c5
---
visualize_spatial_association(gdf_INDICATOR2, W, '2019')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 504
id: e0BKZBhsLpIh
outputId: 2652ebbb-8ce6-473a-8069-14ff19bd2769
---
visualize_spatial_association(gdf_INDICATOR3, W, '2019')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 504
id: g3WWBUSxLo-N
outputId: 6f476dc2-c8f0-417c-d63b-41221c9987b9
---
visualize_spatial_association(gdf_INDICATOR4, W, '2019')
```

+++ {"id": "cuDT3DJPIv3_"}

### 5.3) Spatial inequality

+++ {"id": "vYqTpq11B_Dj"}

#### 5.3.1) Theil index

```{code-cell}
:id: kKw2juNG8vWQ

# Defining a function to return the Their index of a data frame column
def theil_by_col(column):
    return inequality.theil.Theil(column.values).T
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: bp1IwDW69FOy
outputId: 04cdcbc2-7d12-46be-a002-1e5bb330439a
---
# Computing Theil index for each column of the data frame
theil_INDICATOR1  = gdf_INDICATOR1[years].apply(theil_by_col, axis=0).to_frame("Theil_"+INDICATOR1)
theil_INDICATOR1.plot();
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: B4OitH3cHTV9
outputId: f3b3bc9d-6183-4f4d-f39e-867cb493d725
---
theil_INDICATOR2  = gdf_INDICATOR2[years].apply(theil_by_col, axis=0).to_frame("Theil_"+INDICATOR2)
theil_INDICATOR2.plot();
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: gE9BA2VrHar_
outputId: f1d22222-efdb-4d57-c8a5-18d70d7f41be
---
theil_INDICATOR3  = gdf_INDICATOR3[years].apply(theil_by_col, axis=0).to_frame("Theil_"+INDICATOR3)
theil_INDICATOR3.plot();
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: _cndr0UZHjmg
outputId: cde9b47f-dd9c-4719-eb1e-69ceb12f4dbc
---
theil_INDICATOR4  = gdf_INDICATOR4[years].apply(theil_by_col, axis=0).to_frame("Theil_"+INDICATOR4)
theil_INDICATOR4.plot();
```

+++ {"id": "vhKR23ODCJ5G"}

#### 5.3.2) Gini index

```{code-cell}
:id: RFHUdt906nbG

# Defining a function to return the Gini coefficient of a data frame column
def gini_by_col(column):
    return inequality.gini.Gini(column.values).g
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: OCm50GVK70oj
outputId: 915ececa-490c-459b-cd22-fdfce891fe30
---
# Computing Gini index for each column of the data frame
gini_INDICATOR1 = gdf_INDICATOR1[years].apply(gini_by_col, axis=0).to_frame("Gini_"+INDICATOR1)
gini_INDICATOR1.plot();
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: 9hsf18sPMXYa
outputId: 814c3434-7772-46dd-8adc-37902d5d14e5
---
gini_INDICATOR2 = gdf_INDICATOR2[years].apply(gini_by_col, axis=0).to_frame("Gini_"+INDICATOR2)
gini_INDICATOR2.plot();
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 431
id: xM8YCAX_MXG2
outputId: d9ff35f4-dc64-4340-c70c-e473113df74b
---
gini_INDICATOR3 = gdf_INDICATOR3[years].apply(gini_by_col, axis=0).to_frame("Gini_"+INDICATOR3)
gini_INDICATOR3.plot();
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 435
id: j_uj2UyLMW9G
outputId: a5025b8f-4d88-4c10-e59d-5c86164ab3eb
---
gini_INDICATOR4 = gdf_INDICATOR4[years].apply(gini_by_col, axis=0).to_frame("Gini_"+INDICATOR4)
gini_INDICATOR4.plot();
```

+++ {"id": "sGvsI2ScIv4A"}

Let's compute the spatial gini index

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: BWAp9HQ1Iv4B
outputId: 73a404bb-4dc7-4856-f7ae-4c3eae1fdbc0
---
Gini_Spatial(gdf_INDICATOR1['2019'], W).wcg_share
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: RHrfIvMVIv4B
outputId: 636d2775-9e22-4bd5-fa44-5074e87b88ce
---
Gini_Spatial(gdf_INDICATOR1['2019'], W).p_sim
```

+++ {"id": "Tef0jTkyhZtP"}

# 6) Analysis of satellite NTL images

+++ {"id": "o6dlFQfQhvf9"}

## Processing satellite images

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: 1V0xCc89hmc2
outputId: d78b19eb-0da4-459d-dafd-8cf5bf2a1bea
---
# Define the URL of the zip file
url = "https://figshare.com/ndownloader/articles/9828827/versions/7"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Read the content of the response as bytes
    zip_content = BytesIO(response.content)

    # Extract the zip file
    with zipfile.ZipFile(zip_content, 'r') as zip_ref:
        # You can list the files in the zip file if needed
        zip_ref.printdir()

        # Extract the files to a directory (e.g., 'my_extracted_files/')
        zip_ref.extractall('my_extracted_files/')

    print("Zip file has been successfully extracted.")
else:
    print("Failed to retrieve the zip file. Check the URL and your internet connection.")
```

```{code-cell}
:id: e1ntQcGNmjZo

RASTER_DIRECTORY = "/content/my_extracted_files"
```

```{code-cell}
:id: kaRBeUq4moOo

def load_raster(year):
    # Function to open the raster file of a given year. Works for years before and after 2013.
    raster_path = f"{RASTER_DIRECTORY}/Harmonized_DN_NTL_{year}*"
    return (rasterio.open(glob.glob(raster_path)[0]))
```

```{code-cell}
:id: FKkbABcwkMh3

MAPurl = "/content/gdf.geojson"
```

```{code-cell}
:id: 14L_1332kMcg

# The boundaries of states of India are stored in gdf_india36.geojson. The file is loaded using the read_file function from geopandas
polygonsFile = gpd.read_file(MAPurl)

# The bounding box of the vector file previously loaded is extracted using the total_bounds property
polygonsFile_bbox = polygonsFile.total_bounds
```

```{code-cell}
:id: m_BmF4RCkMLX

# The raster file corresponding to the start year is loaded using the open function in rasterio
rasterFileFirst = load_raster(startYear)
# rasterFileFirst = rasterio.open("/content/my_extracted_files/Harmonized_DN_NTL_"+str(startYear)+"_simVIIRS.tif")

# The bounding box of the vector data is used to crop the raster file
rasterFile_windowFirst  = rasterFileFirst.window(*polygonsFile_bbox)
rasterFile_clippedFirst = rasterFileFirst.read(1, window = rasterFile_windowFirst)
```

```{code-cell}
:id: 0rWcblaNmuVq

# The raster file corresponding to the start year is loaded using the open function in rasterio
rasterFileLast = load_raster(endYear)

# The bounding box of the vector data is used to crop the raster file
rasterFile_windowLast  = rasterFileLast.window(*polygonsFile_bbox)
rasterFile_clippedLast = rasterFileLast.read(1, window = rasterFile_windowLast)
```

```{code-cell}
:id: k0krbTQzmuM0

# A dataframe is initialised to store the results
gdf_NTL = polygonsFile.copy()
```

```{code-cell}
:id: ABfber8wmuB6

# A loop runs from the start year to the end year that computes the aggregate nighttime lights radiance for each state
for year in range(startYear, endYear + 1):
    # The raster file of the given year is loaded
    rasterFile = load_raster(year)
    # A mask is a created using the geometry provided in the vector file
    def clean_mask(geom, dataset=rasterFile, **mask_kw):
        mask_kw.setdefault("crop", True)
        mask_kw.setdefault("all_touched", True)
        masked, mask_transform = mask(dataset=dataset, shapes=(geom,),
                                    **mask_kw)
        return masked
    # The mask is a applied and then a summation is performed for computing the aggregate radiance.
    statewise_agg_ntl = polygonsFile.geometry.apply(clean_mask).apply(np.ma.sum)
    # The state wise aggregate radiance of the year is stored in the data frame that was initialised earlier.
    gdf_NTL[str(year)] = statewise_agg_ntl
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 582
id: xOwGA_V5niwh
outputId: 35451490-cfee-4c92-a5a2-c0a733f1a56e
---
gdf_NTL
```

```{code-cell}
:id: 8r2fkL1WnimO

gdf_NTL.to_file("gdf_NTL.geojson", driver="GeoJSON")
```

```{code-cell}
:id: cgUjTsntnibj

# Create long dataframe of NTL
dfWIDE_NTL = gpd.read_file("gdf_NTL.geojson").drop("geometry", axis=1)
dfLONG_NTL = pd.melt(dfWIDE_NTL, id_vars= ["GDLcode", "region"], value_vars=[str(x) for x in range(startYear,endYear +1)])
dfLONG_NTL.columns = ["GDLcode", "region", "year", "NTL"]
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 424
id: yCoyi5pMsCBN
outputId: 513dcaf5-2383-45be-cfd8-e6800d153904
---
dfLONG_NTL
```

```{code-cell}
:id: nTFlrhLRsfpH

# Merge with other indicators
df_NTL_HDI = pd.merge(dfLONG_NTL, df1_INDICATOR1, on=["GDLcode", "region", "year"], how="inner")
df_NTL_HDI = pd.merge(df_NTL_HDI, df1_INDICATOR5, on=["GDLcode", "region", "year"], how="inner")
df_NTL_HDI = pd.merge(df_NTL_HDI, df1_INDICATOR7, on=["GDLcode", "region", "year"], how="inner")
```

```{code-cell}
:id: 1pUYTcwsuD8N

df_NTL_HDI["lnNTL"] = np.log(0.01 + df_NTL_HDI["NTL"])
```

```{code-cell}
:id: 0yiBxOogqNqi

df_NTL_HDI["lnNTLpc"] = np.log((0.01 + df_NTL_HDI["NTL"])*100000000/df_NTL_HDI["pop"])
```

```{code-cell}
:id: 2uszSiT_prg6

df_NTL_HDI["lnGNI"] = np.log(df_NTL_HDI["gnic"]*df_NTL_HDI["pop"])
```

```{code-cell}
:id: CAxnW98lhepu

df_NTL_HDI["GNI"] = df_NTL_HDI["gnic"]*df_NTL_HDI["pop"]
```

```{code-cell}
:id: LF7en2Jxhrd9

df_NTL_HDI["lnGNIpc"] = np.log(df_NTL_HDI["gnic"]*100000000/df_NTL_HDI["pop"])
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 424
id: vr75nDXesffs
outputId: db135f2e-a39c-46c6-9563-fa2cd5a4fdf3
---
df_NTL_HDI
```

```{code-cell}
:id: FkrCfdvZdWM6

# Saving the long form tabular data to a csv file
df_NTL_HDI.to_csv("df_NTL_HDI.csv", index = False)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 300
id: LYDFl_SfrXX6
outputId: 4c80ba01-ef37-4e57-ea15-04f7dc27fce2
---
df_NTL_HDI.describe()
```

```{code-cell}
:id: lfB4Pa60uRkk

# Saving the long form tabular data to a csv file
df_NTL_HDI.to_csv("df_NTL_HDI.csv", index = False)
```

```{code-cell}
:id: DLgtzPGIuW82

# Pivot panel data from long form to wide form
dfWIDE_lnNTL = df_NTL_HDI.pivot_table(
    index=["GDLcode", "region"],
    columns="year",
    values="lnNTL").reset_index(drop=False)
# Make sure the column names are strings
dfWIDE_lnNTL.columns = dfWIDE_lnNTL.columns.astype(str)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 878
id: 3ardkJ9Qu2XJ
outputId: 5a3e08d3-57b5-4f89-c544-87e5b5629d91
---
# Merge with polygonsFile
gdf_lnNTL = pd.merge(polygonsFile, dfWIDE_lnNTL, left_on= ["GDLcode", "region"], right_on= ["GDLcode", "region"], how="inner")
gdf_lnNTL
```

```{code-cell}
:id: 3xcIjmUtuWzU

# Writing the geo data frame of state wise log nighttime lights to a geojson file.
gdf_lnNTL.to_file("gdf_lnNTL.geojson", driver="GeoJSON")
```

```{code-cell}
:id: KxtAZFyljn8M

# Pivot panel data from long form to wide form
dfWIDE_lnNTLpc = df_NTL_HDI.pivot_table(
    index=["GDLcode", "region"],
    columns="year",
    values="lnNTLpc").reset_index(drop=False)
# Make sure the column names are strings
dfWIDE_lnNTLpc.columns = dfWIDE_lnNTLpc.columns.astype(str)
# Merge with polygonsFile
gdf_lnNTLpc = pd.merge(polygonsFile, dfWIDE_lnNTLpc, left_on= ["GDLcode", "region"], right_on= ["GDLcode", "region"], how="inner")
gdf_lnNTLpc.to_file("gdf_lnNTLpc.geojson", driver="GeoJSON")
```

```{code-cell}
:id: 4qTyEoykg6fp

# Pivot panel data from long form to wide form
dfWIDE_GNI = df_NTL_HDI.pivot_table(
    index=["GDLcode", "region"],
    columns="year",
    values="GNI").reset_index(drop=False)
# Make sure the column names are strings
dfWIDE_GNI.columns = dfWIDE_GNI.columns.astype(str)
# Merge with polygonsFile
gdf_GNI = pd.merge(polygonsFile, dfWIDE_GNI, left_on= ["GDLcode", "region"], right_on= ["GDLcode", "region"], how="inner")
gdf_GNI.to_file("gdf_GNI.geojson", driver="GeoJSON")
```

```{code-cell}
:id: ioLOTFFgjkf_

# Pivot panel data from long form to wide form
dfWIDE_lnGNIpc = df_NTL_HDI.pivot_table(
    index=["GDLcode", "region"],
    columns="year",
    values="lnGNIpc").reset_index(drop=False)
# Make sure the column names are strings
dfWIDE_lnGNIpc.columns = dfWIDE_lnGNIpc.columns.astype(str)
# Merge with polygonsFile
gdf_lnGNIpc = pd.merge(polygonsFile, dfWIDE_lnGNIpc, left_on= ["GDLcode", "region"], right_on= ["GDLcode", "region"], how="inner")
gdf_lnGNIpc.to_file("gdf_lnGNIpc.geojson", driver="GeoJSON")
```

+++ {"id": "E95X3t6Zh32x"}

## Visualizing NTL

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 486
id: XYnNb2MZh7nk
outputId: dd46e7ec-add7-4e2a-f05d-d4ff316bdb08
---
# A figure is initialized with 2 plots.
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12,8))

# The nighttime lights around India for the start year is added
im1 = ax1.imshow(rasterFile_clippedFirst, extent=polygonsFile_bbox[[0,2,1,3]], vmin=0, vmax=63, cmap="magma")
# State boundaries are overlayed
polygonsFile.boundary.plot(ax=ax1, color="skyblue", linewidth = 0.4)
# Axis is added
cx.add_basemap(ax=ax1, crs=polygonsFile.crs.to_string(), source = cx.providers.CartoDB.DarkMatterOnlyLabels, attribution=False)

divider1 = make_axes_locatable(ax1)
cax1 = divider1.append_axes("right", size="5%", pad=0.05)
cbar1 = plt.colorbar(im1, cax=cax1)

ax1.set_xlabel("Longitude")
ax1.set_ylabel("Latitude")
# Title of the plot is added
ax1.set_title("(a) Nighttime lights in " + str(startYear))
ax1.set_axis_off()

# The nighttime lights around India for the last year is plotted
im2 = ax2.imshow(rasterFile_clippedLast, extent=polygonsFile_bbox[[0,2,1,3]], vmin=0, vmax=63, cmap="magma")
# State boundaries are overlayed
polygonsFile.boundary.plot(ax=ax2, color="skyblue", linewidth = 0.4)
# Axis is added
cx.add_basemap(ax=ax2, crs=polygonsFile.crs.to_string(), source = cx.providers.CartoDB.DarkMatterOnlyLabels, attribution=False)

divider2 = make_axes_locatable(ax2)
cax2 = divider2.append_axes("right", size="5%", pad=0.05)
cbar2 = plt.colorbar(im2, cax=cax2)

ax2.set_xlabel("Longitude")
ax2.set_ylabel("Latitude")
# Title of the plot is added

ax2.set_title("(b) Nighttime lights in "+str(endYear))
ax2.set_axis_off()

plt.tight_layout()
plt.savefig("NTL.png",dpi=300, bbox_inches="tight")
plt.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 512
id: PCiCZ0Y6wd0V
outputId: 6a434715-93af-4722-e682-5e65e5966019
---
# Static plot of (log) NTL for the initial and final year

# A figure is initialized
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12,8))

# The plot of the start year is added
gdf_lnNTL.plot(column= str(startYear), scheme="BoxPlot", cmap="magma", edgecolor="darkgrey", legend=True, ax=axes[0], legend_kwds={"bbox_to_anchor":(0.88, 0.30)})
cx.add_basemap(ax=axes[0], crs=gdf_lnNTL.crs.to_string(), source = cx.providers.CartoDB.DarkMatterNoLabels,  attribution=False)
cx.add_basemap(ax=axes[0], crs=gdf_lnNTL.crs.to_string(), source = cx.providers.CartoDB.DarkMatterOnlyLabels,  attribution=False)

# The plot of the end year is added.
gdf_lnNTL.plot(column= str(endYear),  scheme="BoxPlot", classification_kwds={"bins":[1, 2, 4, 16]}, cmap="magma", edgecolor="darkgrey", legend=True, ax=axes[1], legend_kwds={"bbox_to_anchor":(0.88, 0.30)})
cx.add_basemap(ax=axes[1], crs=gdf_lnNTL.crs.to_string(), source = cx.providers.CartoDB.DarkMatterNoLabels,  attribution=False)
cx.add_basemap(ax=axes[1], crs=gdf_lnNTL.crs.to_string(), source = cx.providers.CartoDB.DarkMatterOnlyLabels,  attribution=False)

plt.tight_layout()
axes[0].axis("off")
axes[1].axis("off")
axes[0].set_title("(a) Log of NTL in " + str(startYear))
axes[1].set_title("(b) Log of NTL in " + str(endYear))

#plt.savefig("fig_map_lnNTL.png",dpi=300, bbox_inches="tight")
plt.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: Nj-MRGkDr3Ka
outputId: fdf0784a-0168-4da9-fb93-8f57b99c12cd
---
fig0 = px.line(df_NTL_HDI, x = "year", y = "lnNTLpc", color = "region")
fig0.show(renderer="colab")
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: MMCRj7-ryePu
outputId: 88374d85-7ab0-4cc3-ba78-4d902fd60ae6
---
# Regional time series of (log) nighttime lights
fig0 = px.line(df_NTL_HDI, x = "year", y = "lnNTL", color = "region")
fig0.show(renderer="colab")
```

+++ {"id": "BgOxlHsLiMhI"}

## Exploring NTL and GNI

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 424
id: XyJX0PggoMGC
outputId: df66d58d-dc5d-44cd-d00b-ef670db176b6
---
df_NTL_HDI
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: BOv3cz8My-jZ
outputId: 7ceb28e5-67b2-4238-c0fb-5ba6cfe6dcf7
---
fig1 = px.line(df_NTL_HDI, x = "year", y = "lnGNI", color = "region")
fig1.show(renderer="colab")
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: xQcuzNL1tDQv
outputId: 832615cd-8247-46ff-f3d3-c357ad16c0b9
---
fig1 = px.line(df_NTL_HDI, x = "year", y = "lnNTL", color = "region")
fig1.show(renderer="colab")
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: QnuliqJ2zWUX
outputId: a3745966-6fbb-4687-84df-00e2c6a8e605
---
# Interactive scatter plot and regression line of the NTL-GDP relationship
fig3 = px.scatter(data_frame= df_NTL_HDI,
                                x = "lnNTL",
                                y = "lnGNI",
                                #range_x = [6, 16.5],
                                #range_y = [12, 22],
                                hover_name ="region",
                                #text = "selectedRegion",
                                animation_frame = "year",
                                trendline ="ols",
                                #marginal_x = "histogram",
                                #marginal_y =" histogram"
                                )

fig3.show(renderer="colab")
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 2Ir7KS6GScKz
outputId: 90dc5dd0-29f0-41a9-94b5-06165e687706
---
# Interactive scatter plot and regression line of the NTL-GDP relationship
fig4 = px.scatter(data_frame= df_NTL_HDI,
                                x = "lnNTL",
                                y = "lnGNI",
                                #range_x = [6, 16.5],
                                #range_y = [12, 22],
                                hover_name ="region",
                                #text = "selectedRegion",
                                #animation_frame = "year",
                                trendline ="ols",
                                #marginal_x = "histogram",
                                #marginal_y =" histogram"
                                )

fig4.show(renderer="colab")
```

+++ {"id": "t8SIkLcPzyyG"}

## NTL-GNI panel relationship

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 455
id: jLdO55Q80eBX
outputId: 5b644773-b57a-4173-e398-d4d8e809410c
---
# Setup the panel data indices
#df_panel = pd.read_csv("df_NTL_HDI.csv").set_index(["region", "year"])
#df_panel
```

```{code-cell}
:id: N-dbJsi_z0Zs

# Performing panel data regressions to find the relationship between nighttime lights and subnational GDP.
#table = {
#    "(1) Pooled":    PooledOLS.from_formula(formula  = "lnGNI ~ 1 + lnNTL", data=df_panel).fit(cov_type="clustered"),
#    "(2) Within":    PanelOLS.from_formula(formula   = "lnGNI ~ 1 + lnNTL + EntityEffects + TimeEffects",  drop_absorbed=True, data=df_panel).fit(cov_type="clustered"),
#    "(3) Between":   BetweenOLS.from_formula(formula = "lnGNI ~ 1 + lnNTL", data=df_panel).fit(cov_type="clustered"),
#}
```

```{code-cell}
:id: yMospNP70SGp

# Generating a summary table of the regressions.
#compare(table).summary
```

+++ {"id": "OU2igAUJb4oF"}

## NTL and GNI inequality dynamics

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 436
id: 2pGFEMO3eT9t
outputId: dfea7720-6739-4d38-964d-b8c2a83e94f5
---
ax = gdf_NTL[years].apply(gini_by_col, axis=0).to_frame("Gini_NTL").plot()
ax.set_ylim(0, 0.70)
plt.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 436
id: A2s6FDfnffqI
outputId: 2f69163a-8802-4905-b585-ba4cd3c4ec0e
---
ax = gdf_GNI[years].apply(gini_by_col, axis=0).to_frame("Gini_GNI").plot()
ax.set_ylim(0, 0.70)
plt.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 436
id: W5AR3we3iv9b
outputId: 8b30b6a5-dd42-4931-8274-d1ae4c9f524d
---
ax = gdf_lnNTLpc[years].apply(gini_by_col, axis=0).to_frame("Gini_lnNTLpc").plot()
ax.set_ylim(0, 0.20)
plt.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 436
id: zfphiTKhj4xN
outputId: f21ffc18-fb4a-4cf2-9c56-749a4c0ba76c
---
ax = gdf_lnGNIpc[years].apply(gini_by_col, axis=0).to_frame("Gini_lnGNIpc").plot()
ax.set_ylim(0, 0.20)
plt.show()
```

```{code-cell}
:id: GC1gGHnKNCod


```
