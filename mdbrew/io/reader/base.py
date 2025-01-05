from pathlib import Path
from typing import TextIO, Generator, List
from abc import abstractmethod, ABCMeta
from itertools import islice

from mdbrew._core import MDState


def str_to_idx(s: str) -> int | slice:
    return int(s) if ":" not in s else slice(*(int(p) if p else None for p in s.split(":")[:3]))


class BaseReader(metaclass=ABCMeta):
    def __init__(self, filepath: str, **kwargs):
        self._filepath = Path(filepath)
        self._file = None
        self._kwargs = kwargs

    def __repr__(self):
        return f"Reader(fmt={self.fmt})"

    def __enter__(self):
        self._file = self.filepath.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()
            self._file = None

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

    def get_frame_offsets(self, stop: int | None = None) -> List[int]:
        if self._file is None:
            raise RuntimeError("File is not open. Use 'with' statement.")
        frame_offsets = []
        while True:
            try:
                frame_offsets.append(self._get_frame_offset(file=self._file))
                if stop and len(frame_offsets) >= stop:
                    break
            except EOFError:
                break
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {e}")
        return frame_offsets

    def generate(self) -> Generator[MDState, None, None]:
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

    def iread(self, frames: int | str = ":") -> Generator[MDState, None, None]:
        if self._file is None:
            raise RuntimeError("File is not open. Use 'with' statement.")

        idx = str_to_idx(str(frames))

        # Parse slice first to get stop
        is_int = isinstance(idx, int)
        start = idx if is_int else idx.start or 0
        stop = (start + 1) if is_int else (idx.stop or None)

        # Get total frames
        frame_offsets = self.get_frame_offsets(stop=stop)
        nframes = len(frame_offsets)

        # Calculate actual start with nframes
        start = (idx if idx >= 0 else nframes + idx) if is_int else idx.start or 0
        stop = (start + 1) if is_int else (idx.stop or nframes)
        step = 1 if is_int else (idx.step or 1)

        # Validate ranges
        if not 0 <= start < nframes or stop > nframes:
            raise ValueError(f"frames [{start}, {stop}) exceed range [0, {nframes}).")

        self._file.seek(0)
        for offset in frame_offsets[start:stop:step]:
            self._file.seek(offset)
            yield self._make_mdstate(self._file)

    def read(self, frames: int | str = ":") -> List[MDState]:
        with self:
            return list(self.iread(frames))
