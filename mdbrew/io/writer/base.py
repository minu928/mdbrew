from pathlib import Path
from typing import List
from dataclasses import ABCMeta, abstractmethod

from mdbrew._core.mdstate import MDState


class BaseReader(metaclass=ABCMeta):
    def __init__(self, filepath: str, **kwargs):
        self._filepath = Path(filepath)
        self._file = None
        self._kwargs = kwargs

    def __repr__(self):
        return f"Writer(fmt={self.fmt})"

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

    def write(self, mdstaes: MDState | List[MDState]) -> List[MDState]:
        if isinstance(mdstaes, MDState):
            mdstaes = [mdstaes]
        elif not isinstance(mdstaes[0], MDState):
            raise ValueError(f"mdstates does not contains MDState. {type(mdstaes)}")
        pass
