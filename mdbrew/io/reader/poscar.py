from typing import TextIO

from mdbrew._core.mdstate import MDState
from mdbrew.io.reader.base import BaseReader


class POSCARReader(BaseReader):
    fmt = "poscar"

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError

        # Scale factor
        scale = float(file.readline().strip())

        # Box vectors
        box = [file.readline().split() for _ in range(3)]
        if scale != 1.0:
            box = [[float(x) * scale for x in row] for row in box]

        # Elements and counts
        elements = file.readline().split()
        element_counts = file.readline().split()
        atoms = [[element] for element, count in zip(elements, element_counts) for _ in range(int(count))]

        # Skip coordinate type
        next(file)

        # Positions -
        natoms = sum(int(count) for count in element_counts)
        coords = [file.readline().split() for _ in range(natoms)]

        return MDState(atom=atoms, coord=coords, box=box, atomid=range(natoms))

    def _get_frame_offset(self, file):
        frame_offset = file.tell()
        if not file.readline().strip():
            raise EOFError
        file.readline()  # line: scale
        [file.readline().split() for _ in range(3)]  # line: box
        file.readline()  # line: element
        element_counts = file.readline().split()  # line: count
        file.readline()  # line: coord types
        natoms = sum(int(count) for count in element_counts)
        [file.readline() for _ in range(natoms)]
        return frame_offset
