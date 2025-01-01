from typing import TextIO
from collections import defaultdict

import numpy as np

from mdbrew.io.reader.base import BaseReader
from mdbrew._core.mdstate import MDState


PROPERTY_SLICES = {
    "atomid": slice(6, 11),
    "atom": slice(12, 16),
    "residue": slice(17, 21),
    "residueid": slice(22, 26),
    "x": slice(30, 38),
    "y": slice(38, 46),
    "z": slice(46, 54),
    "charge": slice(79, 81),
}


def parse_physicsline(line: str):
    physical_data = {}
    for p in line.split(","):
        p = p.strip()
        if p.startswith("E"):
            physical_data["energy"] = float(p.split("=")[-1])
    return physical_data


def parse_boxline(line: str):
    if line.startswith("CRYST1"):
        try:
            return np.diag(np.array(line.split()[1:4], dtype=float))
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid box line format: {e}")
    raise NotImplementedError("Only CRYST1 format is supported")


class PDBReader(BaseReader):
    fmt = "pdb"

    def _make_mdstate(self, file: TextIO):
        line = file.readline().strip()
        if not line:
            raise EOFError
        if line.startswith("TITLE"):
            line = file.readline()
        if line.startswith("AUTHOR"):
            line = file.readline()
        if line.startswith("REMARK"):
            physics = parse_physicsline(line=line)
        box = parse_boxline(line=file.readline())
        data = defaultdict(list)
        while not (line := file.readline()).startswith("END"):
            for prop, _slice in PROPERTY_SLICES.items():
                if prop_data := line[_slice].strip():
                    data[prop].append(prop_data)
        data["coord"] = np.column_stack([data.pop("x"), data.pop("y"), data.pop("z")]).astype(float)
        return MDState(**data, box=box, **physics)

    def _get_frame_offset(self, file):
        frame_offset = file.tell()
        line = file.readline().strip()
        if not line:
            raise EOFError
        if line.startswith("TITLE"):
            line = file.readline()
        if line.startswith("AUTHOR"):
            line = file.readline()
        if line.startswith("REMARK"):
            line = file.readline()
        file.readline()
        while not (line := file.readline()).startswith("END"):
            pass
        return frame_offset
