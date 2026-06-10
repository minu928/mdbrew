import numpy as np

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

    def __getitem__(self, key):
        return MDState(
            box=self.box,
            position=self.position[key] if self.position is not None else None,
            velocity=self.velocity[key] if self.velocity is not None else None,
            atom=self.atom[key] if self.atom is not None else None,
            atomid=self.atomid[key] if self.atomid is not None else None,
            residue=self.residue[key] if self.residue is not None else None,
            residueid=self.residueid[key] if self.residueid is not None else None,
        )

    def __add__(self, other: "MDState") -> "MDState":
        def cat(a, b):
            if a is None and b is None:
                return None
            if a is None:
                return b
            if b is None:
                return a
            return np.concatenate([a, b])

        return MDState(
            box=self.box,
            position=cat(self.position, other.position),
            velocity=cat(self.velocity, other.velocity),
            atom=cat(self.atom, other.atom),
            atomid=cat(self.atomid, other.atomid),
            residue=cat(self.residue, other.residue),
            residueid=cat(self.residueid, other.residueid),
        )

    def __radd__(self, other):
        if other is None:
            return self
        return self.__add__(other)

    def __len__(self):
        return len(self.atom)

    def reoder_atomid(self):
        self.atomid = np.arange(1, len(self.atom) + 1)

    def delete(self, key) -> "MDState":
        mask = np.ones(len(self.atom), dtype=bool)
        mask[key] = False
        return self[mask]

    def wrap(self):
        lx, ly, lz = np.diag(self.box)
        self.position[:, 0] %= lx
        self.position[:, 1] %= ly
        self.position[:, 2] %= lz
        return self
