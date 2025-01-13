import re
from collections import defaultdict

from ._color import _color
from ._mass import _mass
from ._radii import _radii


class NotAtomInPeriodicTable(Exception):
    def __init__(self, atom):
        super().__init__(f"Atom({atom}) is not included in periodic table.")


def get_color(atom: str):
    if atom not in _color:
        raise NotAtomInPeriodicTable(atom=atom)
    return _color.get(atom)


def get_mass(atom: str):
    if atom not in _mass:
        raise NotAtomInPeriodicTable(atom=atom)
    return _mass.get(atom)


def get_radii(atom: str):
    if atom not in _radii:
        raise NotAtomInPeriodicTable(atom=atom)
    return _radii.get(atom)


def parse_formula(formula: str, *, is_summation: bool = True) -> dict[str, int]:
    pattern = r"([A-Z][a-z]?)(\d*)"
    elements = re.findall(pattern, formula)
    result = defaultdict(int)
    if is_summation:
        for element, count in elements:
            count = int(count) if count else 1
            result[element] += count
    return dict(result)


def calculate_molecularweight(element_dict):
    results = 0.0
    for atom, numb in element_dict.items():
        mass = get_mass(atom=atom)
        results += numb * mass
    return results
