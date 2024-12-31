def str_to_slice(s: str) -> slice:
    """Convert string representation to slice object.

    Args:
        s (str): String in format "start:stop:step" or their subsets like "::", "::-1", "::2"

    Returns:
        slice: A slice object

    Examples:
        >>> str_to_slice(":") -> slice(None, None, None)
        >>> str_to_slice("::2") -> slice(None, None, 2)
        >>> str_to_slice("1:10:2") -> slice(1, 10, 2)
    """
    if not s:
        return slice(None)

    try:
        parts = s.split(":")
        if len(parts) > 3:
            raise ValueError("Too many slice components")

        parts = [int(x) if x else None for x in parts]
        return slice(*parts)
    except ValueError as e:
        raise ValueError(f"Invalid slice format: {s}") from e
