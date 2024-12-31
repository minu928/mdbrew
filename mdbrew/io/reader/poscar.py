from typing import TextIO
from mdbrew.dataclass import MDState
from mdbrew.io.reader.base import BaseReader


class POSCARReader(BaseReader):
    fmt = "poscar"

    def _make_mdstate(self, file: TextIO) -> MDState:
        line = file.readline().strip()
        if not line:
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
        atoms = [element for element, count in zip(elements, element_counts) for _ in range(int(count))]

        # Skip coordinate type
        next(file)

        # Positions -
        natoms = sum(int(count) for count in element_counts)
        coords = [file.readline().split() for _ in range(natoms)]

        return MDState(atom=atoms, coord=coords, box=box)
