from dataclasses import dataclass


AVOGADRO = 6.02214076e23  # None
ELECTRON_CHARGE = 1.602176634e-19  # C
BOHR_RADIUS = 5.29177210544e-11  # m
HATREE_ENERGY = 4.3597447222060e-18  # J


@dataclass
class Prefix:
    """SI prefix  and their symbols"""

    Q = 1e30
    R = 1e27
    Y = 1e24
    Z = 1e21
    E = 1e18
    P = 1e15
    T = 1e12
    G = 1e9
    M = 1e6
    k = 1e3
    h = 1e2
    da = 1e1

    d = 1e-1
    c = 1e-2
    m = 1e-3
    u = 1e-6
    n = 1e-9
    p = 1e-12
    f = 1e-15
    a = 1e-18
    z = 1e-21
    y = 1e-24
    r = 1e-27
    q = 1e-30


# Base SI units
@dataclass
class Length:
    bohr: float = BOHR_RADIUS
    m: float = 1.0
    angstrom: float = 1e-8


@dataclass
class Time:
    s: float = 1.0


@dataclass
class Mass:
    g: float = 1e-3


@dataclass
class Temperature:
    K: float = 1.0


@dataclass
class Charge:
    C = 1.0
    e = ELECTRON_CHARGE


# Derived SI units
@dataclass
class Energy:
    eV: float = ELECTRON_CHARGE
    hatree: float = HATREE_ENERGY
    J: float = 1.0
    cal: float = 4.184


@dataclass
class Force:
    N: float = 1.0
    newton: float = 1.0


@dataclass
class Pressure:
    Pa: float = 1.0
    bar: float = 1e-5
    atm: float = 9.86921e-6
    Torr: float = 7.5006e-3


UNIT_CLASSES = [
    Length,
    Time,
    Mass,
    Temperature,
    Energy,
    Force,
    Pressure,
    Charge,
]

BASE_UNITS = {"Length": "m", "Time": "s", "Mass": "kg", "Current": "A", "Temperature": "K"}

DERIVED_UNITS = {"Force": "N", "Energy": "J", "Power": "W", "Pressure": "Pa"}
