from typing import Iterable, TextIO

from numpy import array, diag, column_stack, savetxt

from mdbrew._core import MDState

from .base import BaseWriter


class LMPSWriter(BaseWriter):
    fmt = "lmps"
    COORD_LABELS = ("x", "y", "z")

    def __init__(self, filepath: str, atom_types: Iterable[str], **kwargs):
        if not atom_types:
            raise ValueError("atom_types cannot be empty (e.g. ['H', 'O'])")
        super().__init__(filepath, **kwargs)
        self._atom_type_ids = {atom: idx for idx, atom in enumerate(map(str, atom_types), 1)}

    @property
    def _required_attributes(self) -> tuple[str, ...]:
        return ("atomid", "atom", "coord", "box")

    def _write_mdstate(self, file: TextIO, mdstate: MDState) -> None:
        atom_types = array([[self._atom_type_ids[atom]] for atom in mdstate.atom.flatten()])
        n_atoms = len(atom_types)
        n_types = len(self._atom_type_ids)

        file.write(f"LMPS By MDBrew\n\n{n_atoms} atoms\n{n_types} atom types\n\n")

        for i, length in enumerate(diag(mdstate.box)):
            dim = self.COORD_LABELS[i]
            file.write(f"0 {length} {dim}lo {dim}hi\n")

        file.write("\n\nAtoms\n\n")
        savetxt(file, column_stack([mdstate.atomid, atom_types, mdstate.coord]), fmt="%d %d %f %f %f")
