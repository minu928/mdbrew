import numpy as np
from typing import List, Literal, Dict, Type
from dataclasses import dataclass
from mdbrew.typing import (
    Force,
    Energy,
    Atom,
    Coord,
    Stress,
    Virial,
    Box,
    Velocity,
    Charge,
    Residue,
    ResidueId,
    AtomId,
    npi64,
    npf64,
    npstr,
)
from mdbrew.utils.space import convert_to_box_matrix

NPDType = Type[npf64] | Type[npi64] | Type[npstr]
PropertyConversions = Dict[str, NPDType]

conversions: PropertyConversions = {
    "force": npf64,
    "energy": npf64,
    "atom": npstr,
    "coord": npf64,
    "stress": npf64,
    "virial": npf64,
    "velocity": npf64,
    "charge": npf64,
    "residue": npstr,
    "residueid": npi64,
    "atomid": npi64,
}


@dataclass(slots=True)
class MDState:
    force: Force = None
    energy: Energy = None
    atom: Atom = None
    atomid: AtomId = None
    coord: Coord = None
    stress: Stress = None
    velocity: Velocity = None
    charge: Charge = None
    virial: Virial = None
    box: Box = None
    residue: Residue = None
    residueid: ResidueId = None

    def __post_init__(self):
        for attr, dtype in conversions.items():
            value = getattr(self, attr)
            if value is not None:
                setattr(self, attr, np.array(value, dtype=dtype))

        if self.box is not None:
            self.box = convert_to_box_matrix(self.box, dtype=npf64)


MDStateList = List[MDState]
MDStateAttr = Literal[
    "force",
    "energy",
    "virial",
    "atom",
    "coord",
    "stress",
    "velocity",
    "charge",
    "box",
    "residue",
    "residueid",
    "atomid",
]
