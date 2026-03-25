"""Arithmetic utilities for MCP CalcForge.

This module provides foundational arithmetic operations, percentage
calculations, and conversion helpers for fractional representations.
"""

from __future__ import annotations

from fractions import Fraction


Number = int | float


def add(a: Number, b: Number) -> Number:
    """Return the sum of two numbers.

    Args:
        a: First addend.
        b: Second addend.

    Returns:
        The result of ``a + b``.
    """
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """Return the difference of two numbers.

    Args:
        a: Minuend.
        b: Subtrahend.

    Returns:
        The result of ``a - b``.
    """
    return a - b


def multiply(a: Number, b: Number) -> Number:
    """Return the product of two numbers.

    Args:
        a: First factor.
        b: Second factor.

    Returns:
        The result of ``a * b``.
    """
    return a * b


def divide(a: Number, b: Number) -> float:
    """Return the quotient of two numbers.

    Args:
        a: Dividend.
        b: Divisor.

    Returns:
        The floating-point result of ``a / b``.

    Raises:
        ZeroDivisionError: If ``b`` equals zero.
    """
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return a / b


def percentage_of(value: Number, percent: Number) -> float:
    """Calculate ``percent`` percent of ``value``.

    Args:
        value: The base value.
        percent: The percentage to apply.

    Returns:
        The computed percentage value as a float.
    """
    return (value * percent) / 100.0


def to_fraction(value: Number) -> Fraction:
    """Convert a number to a reduced :class:`fractions.Fraction`.

    Args:
        value: Numeric value to convert.

    Returns:
        A normalized ``Fraction`` representation of ``value``.
    """
    return Fraction(value).limit_denominator()
