from pathlib import Path
from typing import TextIO, Generator, List
from abc import abstractmethod, ABCMeta

from tqdm import tqdm

from mdbrew._core import MDState


def str_to_idx(s: str) -> int | slice:
    return int(s) if ":" not in s else slice(*(int(p) if p else None for p in s.split(":")[:3]))


def parse_frame_index(frames: int | str) -> tuple[int, int, int]:
    """Parse frame index into start, stop, step.

    Parameters
    ----------
    frames : int or str
        Frame index or slice string (e.g., ":", "1:10:2")

    Returns
    -------
    tuple[int, int, int]
        Parsed (start, stop, step) values
    """
    idx = str_to_idx(str(frames))
    is_int = isinstance(idx, int)

    start = idx if is_int else idx.start or 0
    stop = (start + 1) if is_int else idx.stop or None
    step = 1 if is_int else (idx.step or 1)
    return start, stop, step


def validate_frame_range(start: int, stop: int, nframes: int):
    if not 0 <= start < nframes or stop > nframes:
        raise ValueError(f"frames [{start}, {stop}) exceed range [0, {nframes}).")


class BaseReader(metaclass=ABCMeta):
    def __init__(self, filepath: str, **kwargs):
        self._filepath = Path(filepath)
        self._file = None
        self._kwargs = kwargs
        self._frame_offsets = None

    def __repr__(self):
        return f"Reader(fmt={self.fmt})"

    def __enter__(self):
        self._file = self.filepath.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
            self._file = None
            self._get_frame_offset = None

    @property
    def filepath(self) -> Path:
        return self._filepath

    @property
    @abstractmethod
    def fmt(self) -> str:
        pass

    @abstractmethod
    def _make_mdstate(file: TextIO) -> MDState:
        pass

    @abstractmethod
    def _get_frame_offset(self, file: TextIO) -> int:
        pass

    def generate_states(self) -> Generator[MDState, None, None]:
        if self._file is None:
            raise RuntimeError("File is not open. Use 'with' statement.")
        while True:
            try:
                yield self._make_mdstate(file=self._file)
            except ValueError as e:
                raise ValueError(f"Error reading atom data: {e}") from e
            except EOFError:
                break
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {e}") from e

    def _collect_frame_offsets(self, stop: int | None = None) -> List[int]:
        if self._file is None:
            raise RuntimeError("File is not open. Use 'with' statement.")

        if self._frame_offsets is not None and (stop is None or len(self._frame_offsets) >= stop):
            return self._frame_offsets[:stop] if stop else self._frame_offsets

        self._frame_offsets = []
        self._file.seek(0)
        while True:
            try:
                self._frame_offsets.append(self._get_frame_offset(file=self._file))
                if stop and len(self._frame_offsets) >= stop:
                    break
            except EOFError:
                break
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {e}") from e
        return self._frame_offsets[:stop] if stop else self._frame_offsets

    def calculate_frame_offsets(self, frames: int | str = "0"):
        # Parse initial range
        start, stop, step = parse_frame_index(frames=frames)

        # Get offsets and adjust range
        offsets = self._collect_frame_offsets(stop=stop)
        nframes = len(offsets)

        # Adjust negative indices
        if isinstance(idx := str_to_idx(str(frames)), int):
            start = idx if idx >= 0 else nframes + idx
            stop = start + 1
        else:
            start = start if start >= 0 else nframes + start
            stop = stop or nframes

        # Validate and return
        validate_frame_range(start=start, stop=stop, nframes=nframes)
        return offsets[start:stop:step]

    def iread_at(self, frame_offsets: list[int]) -> Generator[MDState, None, None]:
        if self._file is None:
            raise RuntimeError("File is not open. Use 'with' statement.")

        self._file.seek(0)
        for offset in frame_offsets:
            self._file.seek(offset)
            yield self._make_mdstate(self._file)

    def iread(self, frames: int | str = "0", verbose: bool = False) -> Generator[MDState, None, None]:
        frame_offsets = self.calculate_frame_offsets(frames=frames)
        iterator = self.iread_at(frame_offsets=frame_offsets)
        if verbose:
            iterator = tqdm(iterator, total=len(frame_offsets), desc=f"Read File({self.fmt})")
        return iterator

    def read(self, frames: int | str = "0", *, verbose: bool = False) -> List[MDState]:
        with self:
            return list(self.iread(frames=frames, verbose=verbose))
