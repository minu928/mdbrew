from typing import TextIO

import numpy as np

from mdbrew.type import MDState

from .base import BaseReader


class POSCARReader(BaseReader):
    fmt = "poscar"

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError

        # Scale factor
        scale = float(file.readline().strip())

        # Box vectors (rows are cell vectors, scaled by the universal factor)
        box = np.array([file.readline().split() for _ in range(3)], dtype=float) * scale

        # Elements and counts
        elements = file.readline().split()
        element_counts = file.readline().split()
        atoms = [element for element, count in zip(elements, element_counts) for _ in range(int(count))]

        # Coordinate mode ("Selective dynamics" may precede it)
        mode = file.readline().strip()
        if mode and mode[0] in "sS":
            mode = file.readline().strip()
        is_direct = bool(mode) and mode[0] in "dD"

        # Positions
        natoms = sum(int(count) for count in element_counts)
        coords = np.array([file.readline().split()[:3] for _ in range(natoms)], dtype=float)
        coords = coords @ box if is_direct else coords * scale

        return MDState(atom=atoms, coord=coords, box=box, atomid=range(1, natoms + 1))

    def _get_frame_offset(self, file):
        frame_offset = file.tell()
        if not file.readline().strip():
            raise EOFError
        file.readline()  # line: scale
        [file.readline() for _ in range(3)]  # line: box
        file.readline()  # line: element
        element_counts = file.readline().split()  # line: count
        if (line := file.readline().strip()) and line[0] in "sS":  # line: selective dynamics
            file.readline()  # line: coord mode
        natoms = sum(int(count) for count in element_counts)
        [file.readline() for _ in range(natoms)]
        return frame_offset
