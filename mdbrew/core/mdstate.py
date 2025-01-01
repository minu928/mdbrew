from typing import List
from dataclasses import dataclass, fields

from mdbrew.core.mdarray import MDArray


# fmt: off
class Atom(MDArray): _default_type = str
class AtomId(MDArray): _default_type = int
class Residue(MDArray): _default_type = str
class ResidueId(MDArray): _default_type = int
class Coord(MDArray): ...
class Box(MDArray): ...
class Force(MDArray): ...
class Energy(MDArray): ...
class Velocity(MDArray): ...
class Charge(MDArray): ...
class Stress(MDArray): ...
class Virial(MDArray): ...


# fmt: on
@dataclass(slots=True)
class MDState:
    atom: Atom = None
    atomid: AtomId = None
    residue: Residue = None
    residueid: ResidueId = None
    coord: Coord = None
    box: Box = None
    force: Force = None
    energy: Energy = None
    velocity: Velocity = None
    charge: Charge = None
    stress: Stress = None
    virial: Virial = None

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                setattr(self, field.name, field.type(value))


MDStateList = List[MDState]
