# Documentations about MDBrew

## Quick Start
```python
from mdbrew.io import read


file = "somewhere"
mdstates = read(file, frames="0")
print(f"{mdstates=}")
```

## Detatils
0. [`MDStates`](0_mdstates.md)  
1. [Read the trajectories](1_read.md)  
2. [Write the trajectories](2_write.md)
3. [Operate the `MDState`](3_operations.md)