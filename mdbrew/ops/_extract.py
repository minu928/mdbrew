from typing import Iterator

from mdbrew.core import MDState, MDStateAttr, MDArray


def extract(mdstates: Iterator[MDState], name: MDStateAttr, *, dtype: None = None) -> MDArray:
    _type = MDState.get_type(name=name)
    return _type([mdstate.get(name=name) for mdstate in mdstates], dtype=dtype)
