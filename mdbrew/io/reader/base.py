from pathlib import Path
from typing import TextIO, Generator, List, Optional
from abc import abstractmethod, ABCMeta

from mdbrew.core import MDState, MDStateList


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

    def get_frame_offsets(self, stop: Optional[int] = None) -> List[int]:
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

    def stream(self) -> Generator[MDState, None, None]:
        if self._file is None:
            raise RuntimeError("File is not open. Use 'with' statement.")

        while True:
            try:
                yield self._make_mdstate(file=self._file)
            except ValueError as e:
                raise ValueError(f"Error reading atom data: {e}")
            except EOFError:
                break
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {e}")

    def read(self, frames=None) -> MDStateList:
        with self:
            return list(self.stream())
