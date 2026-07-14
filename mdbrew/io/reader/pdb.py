from typing import TextIO
from collections import defaultdict

from numpy import array, diag, column_stack

from mdbrew.type import MDState

from .base import BaseReader


PROPERTY_SLICES = {
    "atomid": slice(6, 11),
    "atom": slice(12, 16),
    "residue": slice(17, 21),
    "residueid": slice(22, 26),
    "x": slice(30, 38),
    "y": slice(38, 46),
    "z": slice(46, 54),
    "charge": slice(78, 80),
}


def parse_physicsline(line: str):
    physical_data = {}
    for p in line.removeprefix("REMARK").split(","):
        p = p.strip()
        if p.startswith("E"):
            physical_data["energy"] = float(p.split("=")[-1])
    return physical_data


def parse_boxline(line: str):
    if line.startswith("CRYST1"):
        try:
            return diag(array(line.split()[1:4], dtype=float))
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid box line format: {e}")
    raise NotImplementedError("Only CRYST1 format is supported")


class PDBReader(BaseReader):
    fmt = "pdb"

    def _make_mdstate(self, file: TextIO):
        line = file.readline()
        if not line.strip():
            raise EOFError

        # Header: consume any records (TITLE, AUTHOR, REMARK, ...) until CRYST1.
        physics = {}
        while not line.startswith("CRYST1"):
            if line.startswith(("ATOM", "HETATM")):
                raise ValueError("PDB frame has no CRYST1 record before atom records.")
            if line.startswith("REMARK"):
                physics.update(parse_physicsline(line=line))
            line = file.readline()
            if not line:
                raise EOFError
        box = parse_boxline(line=line)

        data = defaultdict(list)
        while (line := file.readline()) and not line.startswith("END"):
            if not line.startswith(("ATOM", "HETATM")):
                continue
            for prop, _slice in PROPERTY_SLICES.items():
                if prop_data := line[_slice].strip():
                    data[prop].append(prop_data)
        data["coord"] = column_stack([data.pop("x"), data.pop("y"), data.pop("z")]).astype(float)
        return MDState(**data, box=box, **physics)

    def _get_frame_offset(self, file):
        frame_offset = file.tell()
        line = file.readline()
        if not line.strip():
            raise EOFError
        while line and not line.startswith("END"):
            line = file.readline()
        return frame_offset
