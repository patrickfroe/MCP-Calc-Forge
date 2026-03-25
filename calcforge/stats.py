"""Statistical and integer utility functions for MCP CalcForge."""

from __future__ import annotations

import math
import statistics


def mean(numbers: list[float]) -> float:
    """Return the arithmetic mean of ``numbers``.

    Args:
        numbers: Sequence of numeric values.

    Returns:
        The arithmetic mean.

    Raises:
        statistics.StatisticsError: If ``numbers`` is empty.
    """
    return statistics.mean(numbers)


def std_dev(numbers: list[float]) -> float:
    """Return the population standard deviation of ``numbers``.

    Args:
        numbers: Sequence of numeric values.

    Returns:
        The population standard deviation.

    Raises:
        statistics.StatisticsError: If ``numbers`` is empty.
    """
    return statistics.pstdev(numbers)


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of two integers."""
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Return the least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def prime_factors(n: int) -> list[int]:
    """Return the prime factorization of ``n`` as a list of primes.

    Args:
        n: Integer greater than 1.

    Returns:
        Prime factors in non-decreasing order.

    Raises:
        ValueError: If ``n`` is less than 2.
    """
    if n < 2:
        raise ValueError("n must be greater than or equal to 2.")

    factors: list[int] = []

    while n % 2 == 0:
        factors.append(2)
        n //= 2

    divisor = 3
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 2

    if n > 1:
        factors.append(n)

    return factors
