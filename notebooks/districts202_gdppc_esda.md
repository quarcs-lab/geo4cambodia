---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  name: python3
  display_name: Python 3
---

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_esda.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# District-level GDP per capita in Cambodia, 1990–2022: exploratory spatial data analysis

Part of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/).

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: KaCeNNdwggMP
outputId: bda9f7ac-739b-4857-f195-72575f9108e1
---
# Adding necessary libraries to Google Colab environment

# Installing the 'contextily' library for adding basemaps to plots
!pip install contextily -q

# Installing the 'splot' library for spatial data visualization
!pip install splot -q

# Installing additional libraries for spatial analysis and visualization
!pip install rasterio -q  # Library for reading and writing raster data
!pip install linearmodels==4.27 -q  # Library for linear models and instrumental variables
!pip install mapclassify -q  # Library for choropleth mapping
!pip install inequality -q  # Library for measuring economic inequality

# Installing the 'mgwr' library for performing geographically weighted regression
!pip install mgwr -q

!pip install statsmodels -q

# The geo4cambodia package loads the data of the observatory (installed locally by `uv sync`)
!pip install geo4cambodia -q
```

```{code-cell}
:id: K602mG1Tgj23

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
from mapclassify import FisherJenks
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
from inequality.gini import Gini
from inequality.theil import Theil
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

# Adjust the plotting bins
import matplotlib.patches as mpatches

# Set the plotting style
sns.set_style('whitegrid')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 964
id: UWL1H5ISVVrN
outputId: 7fc2eeaf-9328-49f8-de6d-205e41099037
---
import geo4cambodia as geo

# One row per district, one column per year of trend400_ln_y, with names and boundaries
wide = geo.load('gdppc', wide='trend400_ln_y')
provinces = geo.units('province')[['geo_id', 'name']].rename(columns={'geo_id': 'parent_id', 'name': 'province'})
names = (geo.units('district')[['geo_id', 'name', 'parent_id']].rename(columns={'name': 'district'})
         .merge(provinces, on='parent_id').drop(columns='parent_id'))
gdf_wide = geo.boundaries('district')[['geo_id', 'geometry']].merge(names, on='geo_id').merge(wide, on='geo_id')
gdf_wide.insert(0, 'id', range(1, len(gdf_wide) + 1))  # integer ids for the spatial weights below
gdf_wide
```

```{code-cell}
:id: nAyqn6Tia4WP

# Identify wide columns
value_vars = [col for col in gdf_wide.columns if col.startswith("trend400_ln_y")]

# Reshape to long
gdf_long = gdf_wide.melt(
    id_vars=[col for col in gdf_wide.columns if col not in value_vars],  # keep IDs + geometry
    value_vars=value_vars,
    var_name="year_var",
    value_name="trend400_ln_y"
)

# Extract year from the variable name
gdf_long["year"] = gdf_long["year_var"].str.extract(r"(\d{4})").astype(int)

# Drop the original wide-style column name
gdf_long = gdf_long.drop(columns="year_var")

# Ensure it's still a GeoDataFrame
gdf_long = gdf_long.set_geometry("geometry")

# Optional: sort for tidy panel structure
gdf_long = gdf_long.sort_values(["id", "year"]).reset_index(drop=True)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 423
id: yPPs9SEibCl5
outputId: 8edf1743-9b58-482a-ca9d-7e12907b6891
---
gdf_long
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: Rk_oApgi9Yoz
outputId: cfc5baec-8ebc-4fd0-89bf-06811177afd5
---
px.strip(
    gdf_long,
    x="trend400_ln_y",
    y="district",
    color="province",
    animation_frame= 'year',
    range_x = [gdf_long["trend400_ln_y"].min(), gdf_long["trend400_ln_y"].max()],
    hover_name="district",
    hover_data=["province","district","trend400_ln_y"]
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 7Qb8Sux1cmnx
outputId: 3b328d1f-3273-401a-e9b8-c3303c921969
---
fig = px.line(
    gdf_long,
    x="year",
    y="trend400_ln_y",
    color="province",
    hover_data=["province", "district","trend400_ln_y"]
)

fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: FQuDVI8Y9tpd
outputId: bb6b3034-fa37-4c0f-a53b-93d53f2c3e13
---
fig, axes = plt.subplots(2, 2, figsize=(30, 20))

gdf_wide.plot(
    column='trend400_ln_y1990',                # Data for coloring
    scheme='FisherJenks',                 # Classification scheme
    k=3,
    cmap='coolwarm',                      # Color map for visualization
    edgecolor='k',                        # Color of edges
    linewidth=0.2,                        # Width of edge lines
    alpha=0.8,                            # Transparency
    legend=True,                          # Show legend
    ax=axes[0,0],                           # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1, 0.5)}  # Legend customization
)
axes[0,0].set_title('Trend of Logged GDP per Capita in 1990', fontsize = 30)
axes[0,0].axis("off")

gdf_wide.plot(
    column='trend400_ln_y2000',                # Data for coloring
    scheme='FisherJenks',                 # Classification scheme
    k=3,
    cmap='coolwarm',                      # Color map for visualization
    edgecolor='k',                        # Color of edges
    linewidth=0.2,                        # Width of edge lines
    alpha=0.8,                            # Transparency
    legend=True,                          # Show legend
    ax=axes[0,1],                           # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1, 0.5)}  # Legend customization
)
axes[0,1].set_title('Trend of Logged GDP per Capita in 2000', fontsize = 30)
axes[0,1].axis("off")

gdf_wide.plot(
    column='trend400_ln_y2010',                # Data for coloring
    scheme='FisherJenks',                 # Classification scheme
    k=3,
    cmap='coolwarm',                      # Color map for visualization
    edgecolor='k',                        # Color of edges
    linewidth=0.2,                        # Width of edge lines
    alpha=0.8,                            # Transparency
    legend=True,                          # Show legend
    ax=axes[1,0],                           # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1, 0.5)}  # Legend customization
)
axes[1,0].set_title('Trend of Logged GDP per Capita in 2010', fontsize = 30)
axes[1,0].axis("off")

gdf_wide.plot(
    column='trend400_ln_y2020',                # Data for coloring
    scheme='FisherJenks',                 # Classification scheme
    k=3,
    cmap='coolwarm',                      # Color map for visualization
    edgecolor='k',                        # Color of edges
    linewidth=0.2,                        # Width of edge lines
    alpha=0.8,                            # Transparency
    legend=True,                          # Show legend
    ax=axes[1,1],                           # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1, 0.5)}  # Legend customization
)
axes[1,1].set_title('Trend of Logged GDP per Capita in 2020', fontsize = 30)
axes[1,1].axis("off")
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 953
id: eCDnawIFeWHe
outputId: dada75aa-661c-4114-edae-11d2086f825e
---
# Visualize spatial data using the explore() method of a GeoDataFrame
gdf_wide.explore(
    # Specify the column to visualize on the map
    column='trend400_ln_y2022',
    # Specify the attributes to display in the tooltip when hovering over map features
    tooltip=['trend400_ln_y2022', 'district', 'province'],
    # Choose the classification scheme for data visualization
    scheme='fisherjenks',
    # Specify the number of classes for classification
    k=3,
    # Choose the colormap for data visualization
    cmap='coolwarm',
    # Specify whether to display a legend
    legend=True,
    # Choose the basemap tiles provider
    tiles='CartoDB positron',
    # Customize the style of the basemap tiles
    style_kwds=dict(color="gray", weight=0.5),
    # Customize the appearance of the legend
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell}
:id: XfGktEPshJJU

Wqueen = weights.Queen.from_dataframe(gdf_wide, ids = 'id')
W_plot = weights.Queen.from_dataframe(gdf_wide)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 807
id: XFPWY-nLebGv
outputId: 72aafb16-eab8-4a46-c3ac-9968e3e5ebbd
---
fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(14,10))
plot_spatial_weights(W_plot, gdf_wide, ax=ax)
cx.add_basemap(ax, crs=gdf_wide.crs.to_string(), source = cx.providers.CartoDB.Positron,           attribution=False)
cx.add_basemap(ax, crs=gdf_wide.crs.to_string(), source = cx.providers.CartoDB.PositronOnlyLabels, attribution=False)
plt.show()
```

```{code-cell}
:id: xmib2lNLhk52

# Define a function to calculate moran's I per year
def moran_by_col(y, w=Wqueen):
    mo = esda.Moran(y, w=w)
    mo_s = pd.Series(
        {"I": mo.I, "I-P value": mo.p_sim},
    )
    return mo_s
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: sVGNuWD4huRp
outputId: f96c6924-5a67-42ff-c58e-8bc519eb0544
---
gdf_wide.columns
```

```{code-cell}
:id: Y8qHAN_ghyKX

columns = ['trend400_ln_y1990',
       'trend400_ln_y1991', 'trend400_ln_y1992', 'trend400_ln_y1993',
       'trend400_ln_y1994', 'trend400_ln_y1995', 'trend400_ln_y1996',
       'trend400_ln_y1997', 'trend400_ln_y1998', 'trend400_ln_y1999',
       'trend400_ln_y2000', 'trend400_ln_y2001', 'trend400_ln_y2002',
       'trend400_ln_y2003', 'trend400_ln_y2004', 'trend400_ln_y2005',
       'trend400_ln_y2006', 'trend400_ln_y2007', 'trend400_ln_y2008',
       'trend400_ln_y2009', 'trend400_ln_y2010', 'trend400_ln_y2011',
       'trend400_ln_y2012', 'trend400_ln_y2013', 'trend400_ln_y2014',
       'trend400_ln_y2015', 'trend400_ln_y2016', 'trend400_ln_y2017',
       'trend400_ln_y2018', 'trend400_ln_y2019', 'trend400_ln_y2020',
       'trend400_ln_y2021', 'trend400_ln_y2022']
array = gdf_wide[columns].to_numpy()
```

```{code-cell}
:id: MeiWuY2qXPuq

moran_dynamics_ratioW = gdf_wide[columns].apply(moran_by_col, axis=0).T
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 487
id: tgFwTdU7iFQT
outputId: 039a5e47-55eb-4549-c106-24465324bbdf
---
# Plot with significance level
def plot_moran_dynamics_with_significance_level(indicator_data):
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

# Plot over the data
plot_moran_dynamics_with_significance_level(moran_dynamics_ratioW)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 808
id: sEijHWMYiIj8
outputId: 8709daf3-b1c8-412f-c056-21ac7c712e24
---
def visualize_spatial_association(gdf_INDICATOR, W, year_var, ax1, ax2):
    """
    Visualize spatial association using Moran's I and Local Indicators of Spatial Association (LISA).

    Parameters:
    - gdf_INDICATOR: GeoDataFrame containing the indicator data for the specified year.
    - W: Spatial weights matrix.
    - year_var: The specific variable name for which spatial association is visualized.
    - ax1, ax2: Matplotlib Axes objects where the plots will be drawn.

    Returns:
    None
    """
    # Extract year from variable name
    year = year_var.replace('trend400_ln_y', '')

    # Calculate global Moran's I
    globalMoran_INDICATOR = Moran(gdf_INDICATOR[year_var], W)
    MoranI_INDICATOR = "{:.2f}".format(globalMoran_INDICATOR.I)

    # Calculate local indicators of spatial association
    localMoran_INDICATOR = Moran_Local(gdf_INDICATOR[year_var], W, permutations=999, seed=12345)

    # Plotting Moran scatterplot
    moran_scatterplot(localMoran_INDICATOR, p=0.01, aspect_equal=False, zstandard=False, ax=ax1)

    # Plotting Local Indicators of Spatial Association (LISA) clusters
    lisa_cluster(localMoran_INDICATOR, gdf_INDICATOR, p=0.01, legend_kwds={'bbox_to_anchor': (0.02, 0.90)}, ax=ax2)

    # Setting labels and titles for the plots
    ax1.set_xlabel('Indicator')
    ax1.set_ylabel('Spatial lag of indicator')
    ax1.set_title(f"(a) Moran scatterplot (Moran's I = {MoranI_INDICATOR})")
    ax2.set_title(f"(b) Spatial clusters and outliers in {year} (p < 0.01)")

# Create a single figure with 1x3 layout for all the years
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))

# Visualize spatial associations for different years, with each subplot in the 1x3 layout
visualize_spatial_association(gdf_wide, Wqueen, 'trend400_ln_y2000', axes[0, 0], axes[0, 1])
visualize_spatial_association(gdf_wide, Wqueen, 'trend400_ln_y2022', axes[1, 0], axes[1, 1])

# Adjust layout for better spacing
plt.tight_layout()

# Save the figure to a file
#plt.savefig('spatial_association_1x2png', dpi=300)

# Show the combined plot
plt.show()
```
