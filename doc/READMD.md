# Documentations about MDBrew

```python
from mdbrew.io import read


file = "somewhere"
mdstates = read(file, frames="0")
print(f"{mdstates=}")
```