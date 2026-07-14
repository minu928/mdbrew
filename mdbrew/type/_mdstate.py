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

# Fields indexed per atom (sliced/concatenated) vs. per frame (passed through).
PER_ATOM_ATTRS = ("atom", "atomid", "residue", "residueid", "coord", "velocity", "force", "charge")
PER_FRAME_ATTRS = ("box", "energy", "stress", "virial")


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
        data = {name: value[key] for name in PER_ATOM_ATTRS if (value := getattr(self, name)) is not None}
        data.update({name: value for name in PER_FRAME_ATTRS if (value := getattr(self, name)) is not None})
        return MDState(**data)

    def __add__(self, other: "MDState") -> "MDState":
        def cat(a, b):
            if a is None and b is None:
                return None
            if a is None:
                return b
            if b is None:
                return a
            return np.concatenate([a, b])

        data = {name: cat(getattr(self, name), getattr(other, name)) for name in PER_ATOM_ATTRS}
        # Per-frame fields are not concatenable; keep self's, falling back to other's.
        data.update(
            {
                name: value
                for name in PER_FRAME_ATTRS
                if (value := getattr(self, name) if getattr(self, name) is not None else getattr(other, name))
                is not None
            }
        )
        return MDState(**data)

    def __radd__(self, other):
        if other is None:
            return self
        return self.__add__(other)

    def __len__(self):
        return len(self.atom)

    def reorder_atomid(self):
        self.atomid = np.arange(1, len(self.atom) + 1)

    reoder_atomid = reorder_atomid  # deprecated misspelled alias

    def delete(self, key) -> "MDState":
        mask = np.ones(len(self.atom), dtype=bool)
        mask[key] = False
        return self[mask]

    def wrap(self):
        # Wrap in fractional space so triclinic cells are handled too
        # (rows of `box` are the cell vectors).
        frac = self.coord @ np.linalg.inv(self.box)
        self.coord[:] = (frac % 1.0) @ self.box
        return self
