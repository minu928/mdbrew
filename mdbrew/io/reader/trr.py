import struct
from typing import BinaryIO

import numpy as np

from mdbrew.type import MDState

from .base import BaseReader

MAGIC = 1993
INT_SIZE = 4
FLOAT_SIZE = 4
DOUBLE_SIZE = 8
DIM = 3


def _read_int(f) -> int:
    return struct.unpack(">i", f.read(INT_SIZE))[0]


def _read_float(f) -> float:
    return struct.unpack(">f", f.read(FLOAT_SIZE))[0]


def _read_double(f) -> float:
    return struct.unpack(">d", f.read(DOUBLE_SIZE))[0]


def _read_string(f) -> str:
    length = _read_int(f)
    padded = (length + 3) & ~3
    return f.read(padded).decode("utf-8").strip("\x00")


def _resolve_floatsize(box_size: int, vir_size: int, pres_size: int, x_size: int, v_size: int, f_size: int, natoms: int) -> int:
    if box_size:
        return box_size // (DIM * DIM)
    if vir_size:
        return vir_size // (DIM * DIM)
    if pres_size:
        return pres_size // (DIM * DIM)
    if x_size:
        return x_size // (natoms * DIM)
    if v_size:
        return v_size // (natoms * DIM)
    if f_size:
        return f_size // (natoms * DIM)
    return FLOAT_SIZE


class TRRReader(BaseReader):
    fmt = "trr"

    def __enter__(self):
        self._file = self.filepath.open("rb")
        return self

    def _read_header(self, file: BinaryIO):
        magic_bytes = file.read(INT_SIZE)
        if not magic_bytes or len(magic_bytes) < INT_SIZE:
            raise EOFError
        magic = struct.unpack(">i", magic_bytes)[0]
        if magic != MAGIC:
            raise ValueError(f"Invalid TRR magic number: {magic}")

        _read_string(file)  # version
        _read_int(file)  # ir_size
        _read_int(file)  # e_size
        box_size = _read_int(file)
        vir_size = _read_int(file)
        pres_size = _read_int(file)
        _read_int(file)  # top_size
        _read_int(file)  # sym_size
        x_size = _read_int(file)
        v_size = _read_int(file)
        f_size = _read_int(file)
        natoms = _read_int(file)
        _read_int(file)  # step
        _read_int(file)  # nre

        floatsize = _resolve_floatsize(box_size, vir_size, pres_size, x_size, v_size, f_size, natoms)
        is_double = floatsize == DOUBLE_SIZE
        read_real = _read_double if is_double else _read_float

        read_real(file)  # time
        read_real(file)  # lambda

        return {
            "natoms": natoms,
            "box_size": box_size,
            "vir_size": vir_size,
            "pres_size": pres_size,
            "x_size": x_size,
            "v_size": v_size,
            "f_size": f_size,
            "read_real": read_real,
        }

    def _make_mdstate(self, file: BinaryIO) -> MDState:
        header = self._read_header(file)
        natoms = header["natoms"]
        read_real = header["read_real"]

        box = None
        if header["box_size"]:
            box = np.array([read_real(file) for _ in range(DIM * DIM)]).reshape(DIM, DIM)

        if header["vir_size"]:
            file.seek(header["vir_size"], 1)
        if header["pres_size"]:
            file.seek(header["pres_size"], 1)

        coord = None
        if header["x_size"]:
            coord = np.array([read_real(file) for _ in range(natoms * DIM)]).reshape(natoms, DIM)

        velocity = None
        if header["v_size"]:
            velocity = np.array([read_real(file) for _ in range(natoms * DIM)]).reshape(natoms, DIM)

        force = None
        if header["f_size"]:
            force = np.array([read_real(file) for _ in range(natoms * DIM)]).reshape(natoms, DIM)

        return MDState(box=box, coord=coord, velocity=velocity, force=force)

    def _get_frame_offset(self, file: BinaryIO) -> int:
        frame_offset = file.tell()
        header = self._read_header(file)
        skip_bytes = (
            header["box_size"]
            + header["vir_size"]
            + header["pres_size"]
            + header["x_size"]
            + header["v_size"]
            + header["f_size"]
        )
        file.seek(skip_bytes, 1)
        return frame_offset
