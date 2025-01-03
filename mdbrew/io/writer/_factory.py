from pathlib import Path
from typing import Iterator

from mdbrew.errors import NotSupportFileFormat
from mdbrew._core import MDState
from mdbrew.io.writer.base import BaseWriter
from mdbrew.io.writer.xyz import XYZWriter
from mdbrew.io.writer.lmps import LMPSWriter
from mdbrew.io.writer.poscar import POSCARWriter
from mdbrew.io.writer.extxyz import EXTXYZWriter


Writer = BaseWriter
WriterRegistry = dict[str, type[BaseWriter]]

registry: WriterRegistry = {
    XYZWriter.fmt: XYZWriter,
    LMPSWriter.fmt: LMPSWriter,
    POSCARWriter.fmt: POSCARWriter,
    EXTXYZWriter.fmt: EXTXYZWriter,
}

WRITER_FORMATS = tuple(registry.keys())


def get_writer(filepath: str, *, fmt: str | None = None, **kwargs) -> Writer:
    if not filepath:
        raise ValueError("Path cannot be empty")
    if fmt is None:
        fmt = Path(filepath).suffix.lstrip(".").lower()
    try:
        opener_cls = registry[fmt]
    except KeyError:
        raise NotSupportFileFormat(fmt=fmt, supports=WRITER_FORMATS)
    return opener_cls(filepath=filepath, **kwargs)


def write(
    filepath: str,
    mdstates: MDState | Iterator[MDState],
    *,
    mode: str = "w",
    fmt: str | None = None,
    **kwargs,
) -> None:
    return get_writer(filepath=filepath, fmt=fmt, **kwargs).write(mdstates=mdstates, mode=mode)
