from re import findall
from typing import TextIO

from numpy import array

from mdbrew.type import MDState

from .base import BaseReader


def parse_properties(line: str):
    pattern = r'(\w+)=("(?:[^"\\]|\\.)*"|[^"\s]+)'
    matches = findall(pattern, line)
    property_size = {}
    results = {}
    for key, value in matches:
        value = value.strip('"')
        if key == "Lattice":
            nums = [float(x) for x in value.split()]
            results["box"] = array(nums).reshape(3, 3)
        elif key in ["stress", "virial"]:
            nums = [float(x) for x in value.split()]
            results[key] = array(nums).reshape(3, 3)
        elif key == "energy":
            results[key] = [float(value)]
        elif key == "Properties":
            props = value.split(":")
            property_size = {props[i]: int(props[i + 2]) for i in range(0, len(props), 3)}
    return property_size, results


class EXTXYZReader(BaseReader):
    fmt = "extxyz"
    PROPERTY_MAP = {
        "species": "atom",
        "positions": "coord",
        "pos": "coord",
        "position": "coord",
        "forces": "force",
        "force": "force",
    }

    def _make_mdstate(self, file: TextIO) -> MDState:
        natoms = file.readline().strip()
        if not natoms:
            raise EOFError
        natoms = int(natoms)
        properties, header = parse_properties(file.readline())
        columns = [(name, size) for name, size in properties.items()]
        data = {name: [] for name, _ in columns}
        col_idx = [sum(size for _, size in columns[:i]) for i in range(len(columns))]
        for _ in range(natoms):
            values = file.readline().split()
            for (name, size), idx in zip(columns, col_idx):
                if name == "species":
                    data[name].append([values[idx]])
                else:
                    data[name].append([float(x) for x in values[idx : idx + size]])
        data.update({self.PROPERTY_MAP[k]: data.pop(k) for k in self.PROPERTY_MAP if k in data})
        return MDState(**data, **header, atomid=range(1, natoms + 1))

    def _get_frame_offset(self, file: TextIO) -> int:
        frame_offset = file.tell()
        line = file.readline()
        if not line:
            raise EOFError
        natoms = int(line.strip())
        file.readline()  # skip property line
        for _ in range(natoms):
            file.readline()
        return frame_offset
