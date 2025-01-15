# Бобер
[![Build and Deploy](https://github.com/AurelienBesnier/bober/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/AurelienBesnier/bober/actions/workflows/python-package-conda.yml)

Cross-platform iRODS gui

### Dependencies
* Python >=3.9
* PySide6 or PyQT6
* python-irodsclient

### To run

Install Miniforge: https://github.com/conda-forge/miniforge

Follow installation instructions. Use default installation settings.

Execute next commands in anaconda prompt.

#### Create a conda environment

```bash
mamba env create -n bober conda/environment.yml
mamba activate bober
pip install -e .
```

#### Run
```bash
cd bober/
python main.py
```
