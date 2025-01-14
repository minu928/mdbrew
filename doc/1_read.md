# How to read the trajectories

## Defaults
```python
from mdbrew.io import read


file = "somewhere"
mdstates = read(file, frames="0")
print(f"{mdstates=}")
```

### You can read any frames using slice.
```python
from mdbrew.io import read


file = "somewhere"
mdstates = read(file, frames=":")  # read all the data
print(f"{mdstates=}")

mdstates = read(file, frames="::2")  # read the data (start=0, end=None, step=2)
print(f"{mdstates=}")

mdstates = read(file, frames=":4:2")  # read the data (start=0, end=4, step=2)
print(f"{mdstates=}")

mdstates = read(file, frames="4")  # read the data at frame 4th (index starts with 0)
print(f"{mdstates=}")
```

### fmt
You can manually set the format of file.

```python
from mdbrew.io import read


file = "somewhere.gro"
mdstates = read(file, frames=":", fmt=None)  # matching the fmt.
print(f"{mdstates=}")

file = "somewhere.gro"
mdstates = read(file, frames=":", fmt="gro")  # directly set fmt.
print(f"{mdstates=}")
```
