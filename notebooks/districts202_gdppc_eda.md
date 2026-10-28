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

<a href="https://colab.research.google.com/github/quarcs-lab/geo4cambodia/blob/main/notebooks/districts202_gdppc_eda.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# District-level GDP per capita in Cambodia, 1990–2022: exploratory data analysis

Part of the [GeoDevelopment Observatory of Cambodia](https://quarcs-lab.github.io/geo4cambodia/).

```{code-cell}
:id: lIYdn1woOS1n

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import requests
```

```{code-cell}
:id: WnfMt9O2YmWk

# The geo4cambodia package loads any dataset of the observatory (installed locally by `uv sync`; installed here in Colab).
# Without the package: pd.read_csv("https://raw.githubusercontent.com/quarcs-lab/geo4cambodia/main/data/district/gdppc.csv")
import importlib.util

if importlib.util.find_spec("geo4cambodia") is None:
    !pip install -q geo4cambodia
```

```{code-cell}
:id: WnfMt9O2YmWl

import geo4cambodia as geo

# District panel: one row per district (geo_id) and year
df = geo.load('gdppc')

# Add district and province names from the GDO unit table
districts = geo.units('district')[['geo_id', 'name', 'parent_id']].rename(columns={'name': 'district'})
provinces = geo.units('province')[['geo_id', 'name']].rename(columns={'geo_id': 'parent_id', 'name': 'province'})
df = df.merge(districts.merge(provinces, on='parent_id').drop(columns='parent_id'), on='geo_id')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 206
id: Q-ODOd67YyAT
outputId: e734b739-6bae-45e3-a9d6-85d75dc2b9d2
---
df.head()
```

+++ {"id": "9j6wLKnAjK22"}

## GDP per capita

```{code-cell}
:id: 1RvmJV-TboEJ

# Describe 'y' by year
df_mean_y = df.groupby('year')['y'].describe().round(2)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 4Nyj9SHmcUoQ
outputId: 62206bd4-5bc2-417c-ad5f-5a3f74b18bec
---
fig = px.line(df_mean_y, x=df_mean_y.index, y=['mean', 'min', 'max'])
fig.update_layout(xaxis_title='Year', yaxis_title='GDP per capita')
fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 7gJrcHZkjTl_
outputId: d4b9ba0e-04d5-4793-87b3-f6ad3379cc02
---
# Calculate quantiles by year
yearly_quantiles = df.groupby('year')['y'].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).unstack()

# Melt the DataFrame to long format
yearly_quantiles_long = yearly_quantiles.reset_index().melt(id_vars='year', var_name='quantile', value_name='y_value')

fig = px.line(yearly_quantiles_long, x='year', y='y_value', color='quantile',
              labels={'quantile': 'Percentile', 'y_value': 'y'},
              title='Time Series of Quantiles of y by Year')

fig.update_layout(xaxis_title='Year', yaxis_title='y')

fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: M3tkfPyTZeH0
outputId: 70cd01b7-0662-4a6c-e91d-9f62b242b633
---
fig = px.box(df, x='year', y='y', hover_name= 'district', hover_data = ['province'],)
fig.update_layout(xaxis_title='Year', yaxis_title='GDP per capita')
fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: vEIKjJnaafRG
outputId: be4c0c5c-21dd-416c-92a3-cf643ac69ad5
---
px.strip(df,
         x = 'y',
         y = 'province',
         range_x= [400, 12700],
         color = 'province',
         hover_name= 'district',
         hover_data = ['province'],
         animation_frame= 'year')
```

+++ {"id": "V3rYug6OjOuk"}

## Trend of GDP per capita

```{code-cell}
:id: vOTGYClKfq5O

# Describe 'trend400_ln_y' by year
df_mean_trend400_ln_y = df.groupby('year')['trend400_ln_y'].describe().round(2)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: VnEcDEk3hEk3
outputId: e6a3fcd6-e899-41b4-fade-bb348cd4507e
---
fig = px.line(df_mean_trend400_ln_y, x=df_mean_trend400_ln_y.index, y=['mean', 'min', 'max'])
fig.update_layout(xaxis_title='Year', yaxis_title='Trend of log GDP per capita')
fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: mLmUzcFxkHVI
outputId: 432a2f57-42ee-44ca-e6ce-abc91b2192b7
---
# Calculate quantiles by year
yearly_quantiles = df.groupby('year')['trend400_ln_y'].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).unstack()

# Melt the DataFrame to long format
yearly_quantiles_long = yearly_quantiles.reset_index().melt(id_vars='year', var_name='quantile', value_name='trend400_ln_y_value')

fig = px.line(yearly_quantiles_long, x='year', y='trend400_ln_y_value', color='quantile',
              labels={'quantile': 'Percentile', 'trend400_ln_y_value': 'trend400_ln_y'},
              title='Time Series of Quantiles of trend400_ln_y by Year')

fig.update_layout(xaxis_title='Year', yaxis_title='trend400_ln_y')

fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: fBxDmHgyhqRW
outputId: 1cd7bd3e-125f-4fde-f24d-63aaba2f41e1
---
fig = px.box(df, x='year', y='trend400_ln_y', hover_name= 'district', hover_data = ['province'],)
fig.update_layout(xaxis_title='Year', yaxis_title='Trend log GDP per capita')
fig.show()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: ZzMvYai2iCi5
outputId: 2070d35d-9dab-45d0-d6a4-b69e5f143bd5
---
px.strip(df,
         x = 'trend400_ln_y',
         y = 'province',
         range_x= [6.10, 9.5],
         color = 'province',
         hover_name= 'district',
         hover_data = ['province'],
         animation_frame= 'year')
```
