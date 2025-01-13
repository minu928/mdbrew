from pathlib import Path
from typing import Iterator

from mdbrew.type import MDState

from .base import BaseWriter
from .xyz import XYZWriter
from .lmps import LMPSWriter
from .poscar import POSCARWriter
from .extxyz import EXTXYZWriter
from .gro import GROWriter


Writer = BaseWriter
WriterRegistry = dict[str, type[BaseWriter]]

registry: WriterRegistry = {
    XYZWriter.fmt: XYZWriter,
    LMPSWriter.fmt: LMPSWriter,
    POSCARWriter.fmt: POSCARWriter,
    EXTXYZWriter.fmt: EXTXYZWriter,
    GROWriter.fmt: GROWriter,
}

SUPPORTED_FORMATS = tuple(registry.keys())


def get_writer(filepath: str, *, fmt: str | None = None, **kwargs) -> Writer:
    if not filepath:
        raise ValueError("Path cannot be empty")
    if fmt is None:
        fmt = Path(filepath).suffix.lstrip(".").lower()
    try:
        opener_cls = registry[fmt]
    except KeyError:
        raise ValueError(f"File formate {fmt} is not supported. We support {SUPPORTED_FORMATS}.")
    return opener_cls(filepath=filepath, **kwargs)


def write(
    filepath: str,
    mdstates: MDState | Iterator[MDState],
    mode: str = "w",
    *,
    fmt: str | None = None,
    verbose: bool = False,
    **kwargs,
) -> None:
    return get_writer(filepath=filepath, fmt=fmt, **kwargs).write(mdstates=mdstates, mode=mode, verbose=verbose)
