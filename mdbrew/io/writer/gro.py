from typing import TextIO

from numpy import column_stack, diag

from mdbrew._core import MDState

from .base import BaseWriter


EXCLUDE_BOX_IDX = -1


def value2line(v) -> str:
    return f"{int(v[0]):5d}{v[1]:5s}{v[2]:5s}{int(v[3]):5d}{float(v[4]):8.3f}{float(v[5]):8.3f}{float(v[6]):8.3f}\n"


class GROWriter(BaseWriter):
    fmt = "gro"

    @property
    def _required_attributes(self) -> tuple[str, ...]:
        return ("residueid", "residue", "atom", "atomid", "coord", "box")

    def _write_mdstate(self, file: TextIO, mdstate: MDState) -> None:
        file.write(f"GRO written by MDBrew\n{len(mdstate.atom)}\n")
        for v in column_stack([getattr(mdstate, attr) for attr in self._required_attributes[:EXCLUDE_BOX_IDX]]):
            file.write(value2line(v=v))
        file.write(" ".join(diag(mdstate.box).flatten().astype(str)))
