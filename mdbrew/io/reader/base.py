from pathlib import Path
from typing import TextIO, Generator, List
from abc import abstractmethod, ABCMeta

from tqdm import tqdm

from mdbrew.type import MDState


def str_to_idx(s: str) -> int | slice:
    return int(s) if ":" not in s else slice(*(int(p) if p else None for p in s.split(":")[:3]))


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

    def calculate_frame_offsets(self, frames: int | str = "0") -> List[int]:
        idx = str_to_idx(str(frames))

        if isinstance(idx, int):
            # A non-negative index lets the offset scan stop early.
            offsets = self._collect_frame_offsets(stop=idx + 1 if idx >= 0 else None)
            nframes = len(offsets)
            i = idx if idx >= 0 else nframes + idx
            if not 0 <= i < nframes:
                raise ValueError(f"frame {idx} out of range for {nframes} frames.")
            return [offsets[i]]

        # Slice: scanning can stop early only for a plain forward slice with
        # non-negative bounds; otherwise the total frame count is needed.
        start, stop, step = idx.start, idx.stop, idx.step
        can_bound = (start or 0) >= 0 and stop is not None and stop >= 0 and (step or 1) > 0
        offsets = self._collect_frame_offsets(stop=stop if can_bound else None)
        return offsets[idx]

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
