from typing import TextIO

from mdbrew.type import MDState
from mdbrew.space import convert_to_box_matrix

from .base import BaseReader

calculate_box_length = lambda lb, ub: float(ub) - float(lb)


def find_column_indices(columns, candidates):
    """Indices of the first candidate column group fully present in ``columns``."""
    for group in candidates:
        if all(col in columns for col in group):
            return [columns.index(col) for col in group]
    return []


class LAMMPSTRJReader(BaseReader):
    fmt = "lammpstrj"

    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)
        self._is_column_inspected = False
        # Each value lists candidate column groups; the first group whose
        # columns are all present in the file wins.
        self.property_dict = {
            "atomid": [["id"]],
            "atom": [["element"], ["type"]],
            "coord": [["xu", "yu", "zu"], ["x", "y", "z"]],
            "force": [["fx", "fy", "fz"]],
            "velocity": [["vx", "vy", "vz"]],
            "charge": [["q"]],
        }
        self._data_indices = {}

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError
        next(file)
        next(file)
        natoms = int(file.readline().strip())

        ndims = file.readline().count("pp")
        box = convert_to_box_matrix([calculate_box_length(*file.readline().split()) for _ in range(ndims)])

        if not self._is_column_inspected:
            columns = file.readline().split()[2:]
            self._data_indices = {
                name: indices
                for name, candidates in self.property_dict.items()
                if (indices := find_column_indices(columns, candidates))
            }
            self._is_column_inspected = True
        else:
            next(file)

        data = {name: [] for name in self._data_indices.keys()}
        for _ in range(natoms):
            atom_values = file.readline().split()
            for name, indices in self._data_indices.items():
                data[name].append(atom_values[indices[0]] if len(indices) == 1 else [atom_values[i] for i in indices])
        return MDState(**data, box=box)

    def modify_property_columns(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, str):
                value = [[value]]
            elif all(isinstance(item, str) for item in value):
                value = [list(value)]
            elif not all(isinstance(col, str) for group in value for col in group):
                raise TypeError(f"{key} must be a column name, a column group, or a list of column groups")
            kwargs[key] = value
        self.property_dict.update(**kwargs)
        self._is_column_inspected = False

    def _get_frame_offset(self, file: TextIO) -> int:
        frame_offset = file.tell()
        if not file.readline().strip():
            raise EOFError
        file.readline()
        file.readline()
        natoms = int(file.readline().strip())
        ndims = file.readline().count("pp")
        [file.readline().split() for _ in range(ndims)]  # line: box
        file.readline()  # line: columns
        [file.readline() for _ in range(natoms)]
        return frame_offset
