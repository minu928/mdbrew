import struct
from datetime import datetime
from typing import BinaryIO

import numpy as np

from mdbrew.type import MDState

from .base import BaseWriter

INT_SIZE = 4
FLOAT_SIZE = 4
DOUBLE_SIZE = 8
DIM = 3

MAGIC = b"CORD"
HEADER_BLOCK_SIZE = 84
UNITCELL_NBYTES = 6 * DOUBLE_SIZE
TITLE_LINE_NBYTES = 80
CHARMM_VERSION = 24

IDX_NFRAMES = 0  # NSET, within the 20-element control (ICNTRL) array
IDX_UNITCELL = 10


def _box_to_unitcell(box) -> tuple:
    """Convert a (3, 3) box matrix to the DCD unit-cell record
    ``[a, cos(gamma), b, cos(beta), cos(alpha), c]``. Cell vectors are the rows."""
    a_vec, b_vec, c_vec = np.asarray(box, dtype=float).reshape(3, 3)
    a, b, c = np.linalg.norm(a_vec), np.linalg.norm(b_vec), np.linalg.norm(c_vec)

    def _cos(u, v, nu, nv):
        return float(np.dot(u, v) / (nu * nv)) if nu and nv else 0.0

    cos_alpha = _cos(b_vec, c_vec, b, c)
    cos_beta = _cos(a_vec, c_vec, a, c)
    cos_gamma = _cos(a_vec, b_vec, a, b)
    return (a, cos_gamma, b, cos_beta, cos_alpha, c)


class DCDWriter(BaseWriter):
    fmt = "dcd"

    def __init__(
        self,
        filepath,
        *,
        timestep: float = 1.0,
        istart: int = 0,
        nsavc: int = 1,
        byteorder: str = "<",
        **kwargs,
    ):
        super().__init__(filepath, **kwargs)
        self._timestep = float(timestep)
        self._istart = int(istart)
        self._nsavc = int(nsavc)
        self._byteorder = byteorder
        self._natoms = None
        self._has_box = None
        self._nframes_written = 0
        self._nset_offset = None

    @property
    def _required_attributes(self) -> tuple[str, ...]:
        return ("coord",)

    def __enter__(self) -> "DCDWriter":
        if self._file is not None:
            return self
        appending = self._mode.startswith("a") and self._filepath.exists() and self._filepath.stat().st_size > 0
        if appending:
            self._file = open(self._filepath, "r+b")
            self._load_header_for_append(self._file)
        else:
            self._file = open(self._filepath, "wb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._file is not None:
            if self._nset_offset is not None:
                self._file.seek(self._nset_offset)
                self._file.write(struct.pack(self._byteorder + "i", self._nframes_written))
            self._file.close()
            self._file = None
        self._natoms = None
        self._has_box = None
        self._nframes_written = 0
        self._nset_offset = None

    def _load_header_for_append(self, file: BinaryIO) -> None:
        file.seek(0)
        head = file.read(INT_SIZE)
        self._byteorder = "<" if struct.unpack("<i", head)[0] == HEADER_BLOCK_SIZE else ">"
        bo = self._byteorder
        file.read(4)  # CORD
        self._nset_offset = file.tell()
        icntrl = struct.unpack(bo + "20i", file.read(20 * INT_SIZE))
        self._nframes_written = icntrl[IDX_NFRAMES]
        self._has_box = bool(icntrl[IDX_UNITCELL])
        file.seek(INT_SIZE, 1)  # closing marker of the control block

        file.seek(INT_SIZE, 1)  # title: opening marker
        ntitle = struct.unpack(bo + "i", file.read(INT_SIZE))[0]
        file.seek(ntitle * TITLE_LINE_NBYTES + INT_SIZE, 1)

        file.seek(INT_SIZE, 1)  # natom: opening marker
        self._natoms = struct.unpack(bo + "i", file.read(INT_SIZE))[0]

        file.seek(0, 2)  # position at end of file to append new frames

    def _write_global_header(self, file: BinaryIO, natoms: int, has_box: bool) -> None:
        bo = self._byteorder

        # --- control block ---
        file.write(struct.pack(bo + "i", HEADER_BLOCK_SIZE))
        file.write(MAGIC)
        self._nset_offset = file.tell()  # NSET is patched with the real count on close
        delta_bits = struct.unpack(bo + "i", struct.pack(bo + "f", self._timestep))[0]
        icntrl = [0] * 20
        icntrl[IDX_NFRAMES] = 0
        icntrl[1] = self._istart
        icntrl[2] = self._nsavc
        icntrl[9] = delta_bits  # DELTA stored as a 32-bit float
        icntrl[IDX_UNITCELL] = 1 if has_box else 0
        icntrl[19] = CHARMM_VERSION
        file.write(struct.pack(bo + "20i", *icntrl))
        file.write(struct.pack(bo + "i", HEADER_BLOCK_SIZE))

        # --- title block ---
        titles = [
            b"Created by MDBrew",
            ("Created " + datetime.now().strftime("%a %b %d %H:%M:%S %Y")).encode("ascii"),
        ]
        block = INT_SIZE + len(titles) * TITLE_LINE_NBYTES
        file.write(struct.pack(bo + "i", block))
        file.write(struct.pack(bo + "i", len(titles)))
        for title in titles:
            file.write(title.ljust(TITLE_LINE_NBYTES, b"\x00")[:TITLE_LINE_NBYTES])
        file.write(struct.pack(bo + "i", block))

        # --- number-of-atoms block ---
        file.write(struct.pack(bo + "i", INT_SIZE))
        file.write(struct.pack(bo + "i", natoms))
        file.write(struct.pack(bo + "i", INT_SIZE))

    def _write_frame(self, file: BinaryIO, mdstate: MDState) -> None:
        bo = self._byteorder

        if self._has_box:
            cell = _box_to_unitcell(mdstate.box)
            file.write(struct.pack(bo + "i", UNITCELL_NBYTES))
            file.write(struct.pack(bo + "6d", *cell))
            file.write(struct.pack(bo + "i", UNITCELL_NBYTES))

        coord = np.asarray(mdstate.coord, dtype=float).reshape(-1, DIM)
        block = coord.shape[0] * FLOAT_SIZE
        f4 = np.dtype("f4").newbyteorder(bo)
        for dim in range(DIM):
            file.write(struct.pack(bo + "i", block))
            file.write(np.ascontiguousarray(coord[:, dim]).astype(f4).tobytes())
            file.write(struct.pack(bo + "i", block))

    def _write_mdstate(self, file: BinaryIO, mdstate: MDState) -> None:
        natoms = np.asarray(mdstate.coord).reshape(-1, DIM).shape[0]

        if self._natoms is None:
            self._natoms = natoms
            if self._has_box is None:
                self._has_box = mdstate.box is not None and np.asarray(mdstate.box).size > 0
            self._write_global_header(file, self._natoms, self._has_box)
        elif natoms != self._natoms:
            raise ValueError(f"All frames must have {self._natoms} atoms, got {natoms}.")

        if self._has_box and (mdstate.box is None or np.asarray(mdstate.box).size == 0):
            raise ValueError("First frame defined a box, but a later frame has none.")

        self._write_frame(file, mdstate)
        self._nframes_written += 1
