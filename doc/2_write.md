# How to write the trajectories

## Defaults
```python
from mdbrew.io import read, write


file = "somewhere"
mdstates = read(file, frames="0")
print(f"{mdstates=}")

write("./some.extxyz", mdstates)
```