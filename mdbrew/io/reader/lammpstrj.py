from typing import TextIO
from mdbrew.dataclass import MDState
from mdbrew.io.reader.base import BaseReader


calculate_box_length = lambda lb, ub: float(ub) - float(lb)


def find_column_indices(columns, targets):
    return [columns.index(col) for col in targets if col in columns]


class LAMMPSTRJReader(BaseReader):
    fmt = "lammpstrj"

    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)
        self._is_column_inspected = False
        self.property_dict = {
            "atom": ["type", "element"],
            "coord": ["x", "y", "z"],
            "force": ["fx", "fy", "fz"],
            "velocity": ["vx", "vy", "vz"],
            "charge": ["q"],
        }
        self._data_indices = {}

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError
        next(file)
        next(file)
        natoms = int(file.readline().strip())

        ndims = file.readline().count("pp")
        box = [calculate_box_length(*file.readline().split()) for _ in range(ndims)]

        if not self._is_column_inspected:
            columns = file.readline().split()[2:]
            data_indices = {
                name: indices
                for name, cols in self.property_dict.items()
                if (indices := find_column_indices(columns, cols))
            }
            self._data_indices = data_indices
            self._is_column_inspected = True
        else:
            next(file)

        data = {name: [] for name in self._data_indices.keys()}
        for _ in range(natoms):
            atom_values = file.readline().split()
            for name, indices in self._data_indices.items():
                data[name].append([atom_values[i] for i in indices])
        return MDState(**data, box=box)

    def modify_property_columns(self, **kwargs):
        for key, value in kwargs.items():
            if not all(isinstance(item, str) for item in value):
                raise TypeError(f"All items in {key} must be strings")
            if not isinstance(value, list):
                kwargs[key] = [value]
        self.property_dict.update(**kwargs)
        self._is_column_inspected = False
