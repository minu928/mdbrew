# MDStates

## MDState
`MDState` contains `numpy.array` data. So, you can use the function from `numpy` package.
```python
from mdbrew import MDState

coords = [[1, 2, 3], [4, 5, 6]]  # array-like data with shape (natoms, 3)
energy = 123123.0  # float
atom = ["H", "O"]

mdstate = MDState(coord=coords, energy=energy, atom=atom)

print(f"{mdstate=}")
print(f"{mdstate.coord.shape=}")
print(f"{mdstate.atom.shape=}")
print(f"{mdstate.energy.shape=}")
```
> mdstate=MDState(data=['atom', 'coord', 'energy'])  
mdstate.coord.shape=(2, 3)  
mdstate.atom.shape=(2,)  
mdstate.energy=Energy(123123.)    


## MDStateAttr
`MDStateAttr` shows the attributes which can be contained in `MDState`
```python
from mdbrew import MDStateAttr

print(MDStateAttr)
```
> typing.Literal['atom', 'atomid', 'residue', 'residueid', 'coord', 'box', 'force', 'energy', 'velocity', 'charge', 'stress', 'virial']