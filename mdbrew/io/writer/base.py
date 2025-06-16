from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import TextIO, Iterable, Sequence

from tqdm import tqdm

from mdbrew.type import MDState, MDStateAttr


class BaseWriter(metaclass=ABCMeta):
    def __init__(self, filepath: str | Path, **kwargs) -> None:
        self._filepath = Path(filepath)
        self._file: TextIO | None = None
        self._strfmt: str | Sequence[str] | None = None
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"Writer(fmt={self.fmt})"

    def __enter__(self) -> "BaseWriter":
        if self._file is None:
            self._file = open(self._filepath, mode=self._mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
            self._mode = "w"

    @property
    def filepath(self) -> Path:
        return self._filepath

    @property
    @abstractmethod
    def fmt(self) -> str:
        pass

    @property
    @abstractmethod
    def _required_attributes(self) -> tuple[str]:
        pass

    @abstractmethod
    def _write_mdstate(self, file: TextIO, mdstate: MDState) -> None:
        pass

    @staticmethod
    def _is_valid_attr(mdstate: MDState, name: MDStateAttr) -> bool:
        attr = getattr(mdstate, name)
        return bool(attr is not None and len(attr))

    def _validate_mdstate(self, mdstate: MDState) -> None:
        if not self._required_attributes:
            raise NotImplementedError("_required_attributes must be implemented and not empty")

        for attr_name in self._required_attributes:
            if not self._is_valid_attr(mdstate, attr_name):
                raise ValueError(f"MDState {attr_name} is empty")

    def write(self, mdstates: MDState | Iterable[MDState], mode: str = "w", *, verbose: bool = False) -> None:
        if isinstance(mdstates, MDState):
            mdstates = list([mdstates])
        elif isinstance(mdstates, Iterable):
            mdstates = list(mdstates)
        else:
            raise ValueError("Input must be MDState or iterable of MDState objects")

        self._mode = mode

        if verbose:
            mdstates = tqdm(mdstates, total=len(mdstates), desc=f"Write File({self.fmt})")

        with self:
            for mdstate in mdstates:
                if not isinstance(mdstate, MDState):
                    raise TypeError("All data must be MDState Type")
                self._validate_mdstate(mdstate=mdstate)
                self._write_mdstate(file=self._file, mdstate=mdstate)
