# MDbrew

<img src="https://img.shields.io/badge/Python-383b40?style=round-square&logo=Python&logoColor=#f5f5f5"/> <img src="https://img.shields.io/badge/Jupyter-383b40?style=round-square&logo=Jupyter&logoColor=#f5f5f5"/>


- VERSION : (3.0.0)

## How to install

```bash
pip install mdbrew
```

## Example
### read
```python
from mdbrew.io import read


filepath = "somewhere/.extxyz"
mdstate = read(filepath, frames=0, fmt="extxyz")
```