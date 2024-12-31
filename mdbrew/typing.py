import numpy as np
from numpy.typing import NDArray


npi64 = np.int64
npf64 = np.float64
npstr = np.str_

Box = NDArray[npf64]
Stress = NDArray[npf64]
Virial = NDArray[npf64]
Coord = NDArray[npf64]
Energy = NDArray[npf64]
Force = NDArray[npf64]
Atom = NDArray[npstr]
AtomId = NDArray[npi64]
Velocity = NDArray[npstr]
Charge = NDArray[npstr]
Residue = NDArray[npstr]
ResidueId = NDArray[npi64]

Vec = NDArray[npf64]

FilePath = str
Frame = int
