from typing import Literal
from dataclasses import dataclass, fields

from ._mdarray import MDArray


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
MDStateAttr = Literal[
    "atom",
    "atomid",
    "residue",
    "residueid",
    "coord",
    "box",
    "force",
    "energy",
    "velocity",
    "charge",
    "stress",
    "virial",
]


@dataclass(slots=True, repr=False)
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

    def __repr__(self):
        return f"MDState(data={[f.name for f in fields(self) if getattr(self, f.name) is not None]})"

    @classmethod
    def get_type(cls, name: MDStateAttr) -> type[MDArray]:
        try:
            field = next(f for f in fields(cls) if f.name == name)
            return field.type
        except StopIteration:
            raise ValueError(f"{name} is not a valid MDState attribute")

    def get(self, name: MDStateAttr) -> MDArray | None:
        value = getattr(self, name, None)
        return value

    def set(self, name: MDStateAttr, value: MDArray | None) -> None:
        if value is not None:
            value = self.get_type(name)(value)
        setattr(self, name, value)
