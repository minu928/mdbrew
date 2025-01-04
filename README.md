# MDbrew

<img src="https://img.shields.io/badge/Python-383b40?style=round-square&logo=Python&logoColor=#f5f5f5"/>

MDBrew is a Python library designed for efficient post-processing and analysis of trajectory and physical property data generated from molecular dynamics simulations.

## Installation
```bash
pip install mdbrew
```
```bash
git clone https://github.com/minu928/mdbrew.git
cd mdbrew
pip install .
```

## Example
```python
from mdbrew.io import read

trjfile = "somewhere.gro"
mdstates = read(trjfile, frames=0)
print(f"{mdstates=}")
```