import math


def log_base(x: float, base: float) -> float:
    return math.log(x, base)


def power(base: float, exponent: float) -> float:
    return math.pow(base, exponent)


def to_scientific_notation(x: float, precision: int = 3) -> str:
    return format(x, f".{precision}e")


def to_binary(n: int) -> str:
    return bin(n)


def from_binary(bin_str: str) -> int:
    return int(bin_str, 2)
