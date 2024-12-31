from pathlib import Path
from typing import Type, Dict
from mdbrew.typing import FilePath
from mdbrew.errors import NotSupportFileFormat
from mdbrew.io.reader.base import BaseReader
from mdbrew.io.reader.xyz import XYZReader
from mdbrew.io.reader.extxyz import EXTXYZReader
from mdbrew.io.reader.poscar import POSCARReader
from mdbrew.io.reader.lammpstrj import LAMMPSTRJReader
from mdbrew.io.reader.gro import GROReader


Reader = BaseReader
ReaderRegistry = Dict[str, Type[BaseReader]]

registry: ReaderRegistry = {
    EXTXYZReader.fmt: EXTXYZReader,
    XYZReader.fmt: XYZReader,
    POSCARReader.fmt: POSCARReader,
    LAMMPSTRJReader.fmt: LAMMPSTRJReader,
    GROReader.fmt: GROReader,
}

SUPPORTED_FORMATS = tuple(registry.keys())


def build(filepath: FilePath, *, fmt: str | None = None) -> Reader:
    if not filepath:
        raise ValueError("Path cannot be empty")
    if fmt is None:
        fmt = Path(filepath).suffix.lstrip(".")
    try:
        opener_cls = registry[fmt]
    except KeyError:
        raise NotSupportFileFormat(fmt=fmt, supports=SUPPORTED_FORMATS)
    return opener_cls(filepath=filepath)
