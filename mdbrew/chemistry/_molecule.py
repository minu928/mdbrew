from mdbrew.unit.SI import AVOGADRO

from typing import Dict, Union

from .atom._func import parse_formula, calculate_molecularweight


ANGSTROM3_TO_CM3 = 1e-24


class Molecule:
    def __init__(self, formula: str) -> None:
        self._formula = formula.strip()
        self._element_dict: Dict[str, int] = parse_formula(formula)
        self._mw: float = calculate_molecularweight(self._element_dict)
        self._natoms: int = sum(self._element_dict.values())

    def __mul__(self, num: Union[int, float]) -> "Molecule":
        if not isinstance(num, (int, float)):
            raise TypeError(f"Multiplication requires a number, got {type(num).__name__}")
        new_formula = "".join(f"{element}{count * num}" for element, count in self._element_dict.items())
        return Molecule(new_formula)

    def __add__(self, molecule: "Molecule") -> "Molecule":
        if not isinstance(molecule, Molecule):
            raise TypeError(f"Addition requires an instance of Molecule, got {type(molecule).__name__}")
        return Molecule(self.formula + molecule.formula)

    def __repr__(self) -> str:
        return self.formula

    @property
    def mw(self) -> float:
        return self._mw

    @property
    def natoms(self) -> int:
        return self._natoms

    @property
    def formula(self) -> str:
        return self._formula

    def calculate_volume(self, density: float) -> float:
        return self.mw / (AVOGADRO * density * ANGSTROM3_TO_CM3)

    def calculate_density(self, volume: float) -> float:
        return self.mw / (volume * AVOGADRO * ANGSTROM3_TO_CM3)

    def calculate_nmols(self, volume: float, density: float) -> float:
        return density * volume * ANGSTROM3_TO_CM3 * AVOGADRO / self.mw
