from pathlib import Path

from mdbrew._core import MDState
from .base import BaseReader
from .xyz import XYZReader
from .extxyz import EXTXYZReader
from .poscar import POSCARReader
from .lammpstrj import LAMMPSTRJReader
from .gro import GROReader
from .lmps import LMPSReader
from .pdb import PDBReader


Reader = BaseReader
ReaderRegistry = dict[str, type[BaseReader]]

registry: ReaderRegistry = {
    EXTXYZReader.fmt: EXTXYZReader,
    XYZReader.fmt: XYZReader,
    POSCARReader.fmt: POSCARReader,
    LAMMPSTRJReader.fmt: LAMMPSTRJReader,
    GROReader.fmt: GROReader,
    LMPSReader.fmt: LMPSReader,
    PDBReader.fmt: PDBReader,
}

SUPPORTED_FORMATS = tuple(registry.keys())


def get_reader(filepath: str, *, fmt: str | None = None) -> Reader:
    if not filepath:
        raise ValueError("Path cannot be empty")
    if fmt is None:
        fmt = Path(filepath).suffix.lstrip(".").lower()
    try:
        opener_cls = registry[fmt]
    except KeyError:
        raise ValueError(f"File formate {fmt} is not supported. We support {SUPPORTED_FORMATS}.")
    return opener_cls(filepath=filepath)


def read(filepath: str, frames: int | str = 0, *, fmt: str | None = None, verbose: bool = False) -> list[MDState]:
    """Read molecular dynamics trajectory file and return list of MDState objects.

    Parameters
    ----------
    filepath : str
        Path to the trajectory file
    frames : int or str, optional
        Frame index or slice string to read. Examples:
        - `-1`              : read last frame (default)
        - `0`               : read first frame
        - `":"` or `None`   : read all frames
        - `":10"`           : read first 10 frames
        - `"10:20"`         : read frames 10 to 19
        - `"::2"`           : read all frames with step 2
    fmt : str or None, optional
        Format of the trajectory file. If None, format is inferred from file extension.
        Supported formats: xyz, lammpstrj

    Returns
    -------
    states : List[MDState]
        List of MDState objects, where each MDState contains:
        - positions : array_like
            Atomic positions
        - cell : array_like
            Simulation cell parameters

    Examples
    --------
    >>> # Read first frame
    >>> states = read("traj.xyz")

    >>> # Read all frames
    >>> states = read("traj.xyz", ":")

    >>> # Read frames 10-19
    >>> states = read("traj.xyz", "10:20")

    >>> # Read LAMMPS trajectory explicitly specifying format
    >>> states = read("dump.lammpstrj", fmt="lammpstrj")
    """
    return get_reader(filepath=filepath, fmt=fmt).read(frames=frames, verbose=verbose)
