from typing import Literal
from dataclasses import dataclass, fields

Unit = str


@dataclass(slots=True)
class MDUnit:
    coord: Unit = None
    box: Unit = None
    force: Unit = None
    energy: Unit = None
    velocity: Unit = None
    charge: Unit = None
    stress: Unit = None
    virial: Unit = None

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                if not isinstance(value, Unit):
                    raise ValueError("type of unit must be string")
                setattr(self, field.name, field.type(value))


MDUnitAttr = Literal["coord", "box", "force", "energy", "velocity", "charge", "stress", "virial"]
