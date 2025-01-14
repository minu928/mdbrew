# Operate the `MDStates`

## Extract the data
Name of data should be in `MDStateAttr`

```python
import mdbrew as md
from mdbrew import MDStateAttr
from mdbrew.io import read

file = "./src/trj/test.extxyz"
mdstates = read(file, frames=":")
print(f"{mdstates=}")
print(f"{MDStateAttr=}")

coord = md.extract(mdstates, name="coord")
print(f"{coord.shape=}")
energy = md.extract(mdstates, name="energy")
print(f"{energy.shape=}")
```

## Where
```python
import mdbrew as md
from mdbrew import MDStateAttr
from mdbrew.io import read

file = "./src/trj/test.extxyz"
mdstates = read(file, frames=":")

ref_mdstate = mdstates[0]

md.where((ref_mdstate.atom == "H") & (ref_mdstate.atomid > 100))
```