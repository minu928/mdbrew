import re
from dataclasses import fields

from mdbrew.unit.SI import UNIT_CLASSES, Prefix


def get_unit_class(unit: str):
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


def calculate_unit_value(unit: str):
    try:
        return float(unit)
    except:
        scale_factor, base_unit = parse_unit(unit=unit)
        unit_class = get_unit_class(base_unit)
        return scale_factor * getattr(unit_class, base_unit)


def tokenize_unit_expression(expression: str) -> list:
    return re.findall(r"[*/^]|[^*/^]+", expression)


def parse_expression(tokens: list) -> float:
    i = 1
    while i < len(tokens):
        if tokens[i] == "^":
            base = calculate_unit_value(tokens[i - 1])
            exponent = float(tokens[i + 1])
            tokens[i - 1 : i + 2] = [base**exponent]
        else:
            i += 1
    result = calculate_unit_value(tokens[0])
    i = 1
    while i < len(tokens):
        if tokens[i] == "/":
            result /= calculate_unit_value(tokens[i + 1])
            i += 2
        elif tokens[i] == "*":
            result *= calculate_unit_value(tokens[i + 1])
            i += 2
        else:
            i += 1
    return result


def evaluate_unit_expression(expression: str) -> float:
    tokens = tokenize_unit_expression(expression)
    return parse_expression(tokens)


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
    if len(seperated_expr) != 2:
        raise ValueError(f"Expression must include one sep({sep}), such as 'km->m'")

    from_expr = seperated_expr[0].strip()
    to_expr = seperated_expr[1].strip()

    factor = evaluate_unit_expression(from_expr) / evaluate_unit_expression(to_expr)
    return clean_number(factor, precision=precision)
