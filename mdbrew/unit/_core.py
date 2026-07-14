import re
from dataclasses import fields

from mdbrew.unit.SI import UNIT_CLASSES, Prefix


def get_unit_class(unit: str):
    # Exact base-unit name first, then the longest valid suffix match.
    for cls in UNIT_CLASSES:
        if any(field.name == unit for field in fields(cls)):
            return cls
    match = _match_base_unit(unit)
    return match[1] if match else None


def _match_base_unit(unit: str) -> tuple[str, type] | None:
    """Longest base unit (across all unit classes) that ends ``unit`` with a
    valid (or empty) SI prefix. Returns ``(base_unit, unit_class)`` or None."""
    best = None
    for cls in UNIT_CLASSES:
        for field in fields(cls):
            name = field.name
            if not unit.endswith(name):
                continue
            prefix = unit[: -len(name)]
            if prefix and not isinstance(getattr(Prefix, prefix, None), (int, float)):
                continue
            if best is None or len(name) > len(best[0]):
                best = (name, cls)
    return best


def parse_unit(unit: str) -> tuple[float, str]:
    """Parse unit string into SI prefix factor and base unit.

    Examples:
        >>> parse_unit("km")
        (1000.0, "m")
        >>> parse_unit("MPa")
        (1e6, "Pa")
    """
    match = _match_base_unit(unit)
    if match is None:
        raise ValueError(f"Unknown unit: {unit}")
    base_unit, _ = match
    prefix = unit[: -len(base_unit)]
    factor = getattr(Prefix, prefix) if prefix else 1.0
    return factor, base_unit


_COEFF_UNIT = re.compile(r"^([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)?\s*(.*)$")


def calculate_unit_value(unit: str):
    try:
        return float(unit)
    except ValueError:
        number, symbol = _COEFF_UNIT.match(unit.strip()).groups()
        coeff = float(number) if number else 1.0
        scale_factor, base_unit = parse_unit(unit=symbol)
        unit_class = get_unit_class(base_unit)
        return coeff * scale_factor * getattr(unit_class, base_unit)


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
