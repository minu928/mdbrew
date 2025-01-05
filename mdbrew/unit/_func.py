from dataclasses import fields

from mdbrew.unit.SI import UNIT_CLASSES, Prefix


def get_unit_class(unit: str):
    """Find appropriate unit class for given base unit."""
    for cls in UNIT_CLASSES:
        if any(unit.endswith(field.name) for field in fields(cls)):
            return cls
    return None


def parse_unit(unit: str) -> tuple[float, str]:
    """Parse unit string into SI prefix factor and base unit.

    Examples:
        >>> parse_unit("km")
        (1000.0, "m")
        >>> parse_unit("MPa")
        (1e6, "Pa")
    """
    # Try to find unit class first
    unit_class = get_unit_class(unit)
    if unit_class is None:
        raise ValueError(f"Unknown unit: {unit}")

    # Find all possible base units from the class
    base_units = [field.name for field in fields(unit_class)]
    matching_base = [bu for bu in base_units if unit.endswith(bu)]
    if not matching_base:
        raise ValueError(f"No matching base unit found for: {unit}")

    # Get the longest matching base unit
    base_unit = max(matching_base, key=len)
    prefix = unit[: -len(base_unit)]

    # Get prefix factor
    if prefix:
        if not hasattr(Prefix, prefix):
            raise ValueError(f"Unknown SI prefix: {prefix}")
        factor = getattr(Prefix, prefix)
    else:
        factor = 1.0

    return factor, base_unit


def clean_number(value: float, precision: int = 10) -> float:
    """Clean number representation for unit conversions."""
    threshold = 10 ** (-precision)  # 동적 임계값 설정
    if abs(value) < threshold or abs(value) > 1 / threshold:
        return float(f"{value:.{precision}e}")
    return float(f"{value:.{precision}g}")


def convert(expr: str, *, sep: str = "->", precision: int = 10):
    """Convert between different units using string expression.

    Examples:
        >>> convert("1km->m")
        1000.0
        >>> convert("1MPa->kPa")
        1000.0
        >>> convert("1angstrom->nm")
        0.1
    """
    seperated_expr = str(expr).split(sep=sep)
    match len(seperated_expr):
        case 2:
            from_unit = seperated_expr[0].strip()
            to_unit = seperated_expr[1].strip()
            # Parse units
            from_factor, from_base = parse_unit(from_unit)
            to_factor, to_base = parse_unit(to_unit)

            # Get unit class
            unit_class = get_unit_class(from_base)
            if unit_class is not get_unit_class(to_base):
                raise ValueError(f"Incompatible units: {from_unit} -> {to_unit}")

            # Apply both SI prefix and base unit conversions
            base_from_factor = getattr(unit_class, from_base)
            base_to_factor = getattr(unit_class, to_base)

            factor = (from_factor * base_from_factor) / (to_factor * base_to_factor)
            return clean_number(factor, precision=precision)

        case _:
            raise ValueError(f"Expression must include one sep({sep}), such as 'km->m'")
