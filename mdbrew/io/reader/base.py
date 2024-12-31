from pathlib import Path
from typing import TextIO, Generator
from abc import abstractmethod, ABCMeta
from mdbrew.typing import FilePath, NDArray
from mdbrew.dataclass import MDState, MDStateList
from mdbrew.utils import str_to_slice


class BaseReader(metaclass=ABCMeta):
    def __init__(self, filepath: FilePath, **kwargs):
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
