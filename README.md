# Бобер
[![Build and Deploy](https://github.com/AurelienBesnier/bober/actions/workflows/python-app.yml/badge.svg)](https://github.com/AurelienBesnier/bober/actions/workflows/python-app.yml)

Cross-platform iRODS gui

### Dependencies
* Python >=3.9
* PySide6 or PyQT6
* python-irodsclient
* natsort

### To run

#### Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install . # or pip install -e.
```

#### Create a conda environment

Install Miniforge: https://github.com/conda-forge/miniforge

Follow installation instructions. Use default installation settings.

Execute next commands in anaconda prompt.

```bash
mamba env create -n bober -f conda/environment.yml
mamba activate bober
pip install -e .
```

#### Run
```bash
cd bober/
python main.py
```
