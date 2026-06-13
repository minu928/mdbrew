import struct
from typing import BinaryIO

import numpy as np

from mdbrew.type import MDState

from .base import BaseReader

INT_SIZE = 4
FLOAT_SIZE = 4
DOUBLE_SIZE = 8
DIM = 3

MAGIC = b"CORD"
HEADER_BLOCK_SIZE = 84
UNITCELL_NBYTES = 6 * DOUBLE_SIZE  # 6 doubles: a, cos(gamma), b, cos(beta), cos(alpha), c

# indices into the 20-element control (ICNTRL) array
IDX_NFRAMES = 0
IDX_NFIXED = 8
IDX_UNITCELL = 10
IDX_CHARMM_VERSION = 19


def _unitcell_to_box(cell) -> np.ndarray:
    """Convert a DCD unit-cell record to a (3, 3) box matrix.

    The record is stored as ``[a, cos(gamma), b, cos(beta), cos(alpha), c]``.
    Some older writers store the angles directly in degrees; both layouts are
    handled. An orthorhombic cell is returned as a clean diagonal matrix.
    """
    a, b, c = float(cell[0]), float(cell[2]), float(cell[5])
    cos_gamma, cos_beta, cos_alpha = float(cell[1]), float(cell[3]), float(cell[4])

    if all(-1.0 <= v <= 1.0 for v in (cos_alpha, cos_beta, cos_gamma)):
        alpha = np.degrees(np.arccos(cos_alpha))
        beta = np.degrees(np.arccos(cos_beta))
        gamma = np.degrees(np.arccos(cos_gamma))
    else:
        alpha, beta, gamma = cos_alpha, cos_beta, cos_gamma

    if all(abs(ang - 90.0) < 1e-4 for ang in (alpha, beta, gamma)):
        return np.diag([a, b, c]).astype(float)

    alpha_r, beta_r, gamma_r = np.radians([alpha, beta, gamma])
    ax = a
    bx = b * np.cos(gamma_r)
    by = b * np.sin(gamma_r)
    cx = c * np.cos(beta_r)
    cy = c * (np.cos(alpha_r) - np.cos(beta_r) * np.cos(gamma_r)) / np.sin(gamma_r)
    cz = np.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    return np.array([[ax, 0.0, 0.0], [bx, by, 0.0], [cx, cy, cz]], dtype=float)


class DCDReader(BaseReader):
    fmt = "dcd"

    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)
        self._header = None

    def __enter__(self):
        self._file = self.filepath.open("rb")
        self._header = self._read_global_header(self._file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._header = None

    def _read_global_header(self, file: BinaryIO) -> dict:
        head = file.read(INT_SIZE)
        if len(head) < INT_SIZE:
            raise EOFError
        byteorder = "<" if struct.unpack("<i", head)[0] == HEADER_BLOCK_SIZE else ">"
        if struct.unpack(byteorder + "i", head)[0] != HEADER_BLOCK_SIZE:
            raise ValueError("Invalid DCD file: leading block size is not 84.")

        magic = file.read(4)
        if magic != MAGIC:
            raise ValueError(f"Invalid DCD magic number: {magic!r}")

        icntrl = struct.unpack(byteorder + "20i", file.read(20 * INT_SIZE))
        file.seek(INT_SIZE, 1)  # closing marker of the control block

        nfixed = icntrl[IDX_NFIXED]
        if nfixed:
            raise NotImplementedError("DCD files with fixed atoms are not supported.")

        # title block: marker, ntitle, ntitle * 80 bytes, marker
        file.seek(INT_SIZE, 1)
        ntitle = struct.unpack(byteorder + "i", file.read(INT_SIZE))[0]
        file.seek(ntitle * 80 + INT_SIZE, 1)

        # number-of-atoms block: marker, natoms, marker
        file.seek(INT_SIZE, 1)
        natoms = struct.unpack(byteorder + "i", file.read(INT_SIZE))[0]
        file.seek(INT_SIZE, 1)

        has_box = bool(icntrl[IDX_UNITCELL])
        coord_block_nbytes = natoms * FLOAT_SIZE + 2 * INT_SIZE
        unitcell_nbytes = (UNITCELL_NBYTES + 2 * INT_SIZE) if has_box else 0

        return {
            "byteorder": byteorder,
            "natoms": natoms,
            "has_box": has_box,
            "nframes": icntrl[IDX_NFRAMES],
            "first_frame_offset": file.tell(),
            "frame_nbytes": unitcell_nbytes + DIM * coord_block_nbytes,
            "coord_dtype": np.dtype("f4").newbyteorder(byteorder),
        }

    def _read_unitcell(self, file: BinaryIO) -> np.ndarray:
        file.seek(INT_SIZE, 1)  # opening marker (48)
        cell = struct.unpack(self._header["byteorder"] + "6d", file.read(UNITCELL_NBYTES))
        file.seek(INT_SIZE, 1)  # closing marker
        return _unitcell_to_box(cell)

    def _read_coord_block(self, file: BinaryIO) -> np.ndarray:
        natoms = self._header["natoms"]
        file.seek(INT_SIZE, 1)  # opening marker (natoms * 4)
        block = np.frombuffer(file.read(natoms * FLOAT_SIZE), dtype=self._header["coord_dtype"])
        file.seek(INT_SIZE, 1)  # closing marker
        return block

    def _make_mdstate(self, file: BinaryIO) -> MDState:
        if len(file.read(INT_SIZE)) < INT_SIZE:
            raise EOFError
        file.seek(-INT_SIZE, 1)

        box = self._read_unitcell(file) if self._header["has_box"] else None

        coord = np.empty((self._header["natoms"], DIM), dtype="f4")
        for dim in range(DIM):
            coord[:, dim] = self._read_coord_block(file)

        return MDState(coord=coord, box=box)

    def _get_frame_offset(self, file: BinaryIO) -> int:
        if file.tell() == 0:
            file.seek(self._header["first_frame_offset"])
        frame_offset = file.tell()
        if len(file.read(INT_SIZE)) < INT_SIZE:
            raise EOFError
        file.seek(frame_offset + self._header["frame_nbytes"])
        return frame_offset
