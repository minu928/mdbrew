from numpy import where

from mdbrew.type import MDState, MDArray, MDStateAttr
from mdbrew.utils.check import check_mdstates


def extract(mdstates: list[MDState], name: MDStateAttr, *, dtype=None) -> MDArray:
    """Extract and stack arrays of specified attribute from MDState list.

    Parameters
    ----------
    mdstates : list[MDState]
        List of MDState objects to extract from.
    name : MDStateAttr
        Name of attribute to extract.
    dtype : np.dtype, optional
        Data type for output array.

    Returns
    -------
    MDArray
        Stacked array of extracted attributes.

    Raises
    ------
    ValueError
        If mdstates is empty or not iterable.
    """
    check_mdstates(mdstates=mdstates)
    _type = MDState.get_type(name=name)
    return _type([mdstate.get(name=name) for mdstate in mdstates], dtype=dtype)


def query(mdstates: list[MDState], what: str, name: MDStateAttr = "atom") -> MDArray[int]:
    """Find atom indices matching specified type in first frame.

    Parameters
    ----------
    mdstates : list[MDState]
        List of MDState objects to search in.
    what : str
        Atom type to search for.

    Returns
    -------
    MDArray[int]
        Indices where atom type matches.

    Raises
    ------
    ValueError
        If mdstates is empty or first state has no atom data.
    TypeError
        If mdstates is not iterable.
    """
    check_mdstates(mdstates=mdstates)
    attr = mdstates[0].get(name=name)
    if attr is None:
        raise ValueError("No atom data in MDState")
    return where(attr.flatten() == what)[0]
