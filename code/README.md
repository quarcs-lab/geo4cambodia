# Code

Data-preparation code for the observatory.

- **Building and validating the published data:** the `geo4cambodia` package in [`../src/geo4cambodia/`](../src/geo4cambodia/). Builders in [`../src/geo4cambodia/build/`](../src/geo4cambodia/build/) turn the originals in [`../raw/`](../raw/) into `data/`, `geo/` and `docs/datasets/`. Run `uv run geo4cambodia build && uv run geo4cambodia validate`. See [`../CONTRIBUTING_DATA.md`](../CONTRIBUTING_DATA.md) to add a dataset.
- **Remote-sensing extraction (Python, Colab):** [Getting remote sensing data in Python](https://colab.research.google.com/drive/1VQFcaKJl0Lz_c_gGrb4FZ2uJvAVseEKp?usp=sharing). Zonal statistics behind the [`env`](../docs/datasets/env.md) dataset.
- **Earth Engine apps:** see [`../apps`](../apps/).
- **Analysis notebooks:** see [`../notebooks`](../notebooks/).
