"""MCP server entrypoint for MCP CalcForge.

This module wires CalcForge math helpers into FastMCP tools and exposes
an HTTP JSON-RPC endpoint.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from fastmcp import FastMCP

from calcforge import algebra, arithmetic, geometry, stats
from calcwerk import utils

mcp = FastMCP("MCP CalcForge")


@mcp.tool()
def add(a: int | float, b: int | float) -> int | float:
    """Add two numbers and return the sum."""
    return arithmetic.add(a, b)


@mcp.tool()
def subtract(a: int | float, b: int | float) -> int | float:
    """Subtract ``b`` from ``a`` and return the result."""
    return arithmetic.subtract(a, b)


@mcp.tool()
def multiply(a: int | float, b: int | float) -> int | float:
    """Multiply two numbers and return the product."""
    return arithmetic.multiply(a, b)


@mcp.tool()
def divide(a: int | float, b: int | float) -> float:
    """Divide ``a`` by ``b`` and return the quotient."""
    return arithmetic.divide(a, b)


@mcp.tool()
def percentage_of(value: int | float, percent: int | float) -> float:
    """Calculate ``percent`` percent of ``value``."""
    return arithmetic.percentage_of(value, percent)


@mcp.tool()
def to_fraction(value: int | float) -> Fraction:
    """Convert a numeric value to its reduced fraction representation."""
    return arithmetic.to_fraction(value)


@mcp.tool()
def circle_area(radius: float) -> float:
    """Calculate the area of a circle."""
    return geometry.circle_area(radius)


@mcp.tool()
def circle_circumference(radius: float) -> float:
    """Calculate the circumference of a circle."""
    return geometry.circle_circumference(radius)


@mcp.tool()
def rectangle_area(a: float, b: float) -> float:
    """Calculate the area of a rectangle."""
    return geometry.rectangle_area(a, b)


@mcp.tool()
def rectangle_perimeter(a: float, b: float) -> float:
    """Calculate the perimeter of a rectangle."""
    return geometry.rectangle_perimeter(a, b)


@mcp.tool()
def triangle_area(base: float, height: float) -> float:
    """Calculate the area of a triangle."""
    return geometry.triangle_area(base, height)


@mcp.tool()
def sphere_volume(radius: float) -> float:
    """Calculate the volume of a sphere."""
    return geometry.sphere_volume(radius)


@mcp.tool()
def cylinder_volume(radius: float, height: float) -> float:
    """Calculate the volume of a cylinder."""
    return geometry.cylinder_volume(radius, height)


@mcp.tool()
def cone_volume(radius: float, height: float) -> float:
    """Calculate the volume of a cone."""
    return geometry.cone_volume(radius, height)


@mcp.tool()
def pyramid_volume(base_area: float, height: float) -> float:
    """Calculate the volume of a pyramid."""
    return geometry.pyramid_volume(base_area, height)


@mcp.tool()
def solve_quadratic(a: float, b: float, c: float) -> tuple[Any, ...]:
    """Solve ``a*x**2 + b*x + c = 0`` and return both roots."""
    return algebra.solve_quadratic(a, b, c)


@mcp.tool()
def solve_linear_system(equations: list[str], variables: list[str]) -> dict[str, Any]:
    """Solve a linear equation system and map each variable to its value."""
    return algebra.solve_linear_system(equations, variables)


@mcp.tool()
def factor_polynomial(expr: str) -> str:
    """Factor a polynomial expression and return it as a string."""
    return algebra.factor_polynomial(expr)


@mcp.tool()
def find_roots(expr: str) -> list[Any]:
    """Find roots for a univariate polynomial expression."""
    return algebra.find_roots(expr)


@mcp.tool()
def mean(numbers: list[float]) -> float:
    """Return the arithmetic mean of the provided numbers."""
    return stats.mean(numbers)


@mcp.tool()
def std_dev(numbers: list[float]) -> float:
    """Return the population standard deviation of the provided numbers."""
    return stats.std_dev(numbers)


@mcp.tool()
def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of two integers."""
    return stats.gcd(a, b)


@mcp.tool()
def lcm(a: int, b: int) -> int:
    """Return the least common multiple of two integers."""
    return stats.lcm(a, b)


@mcp.tool()
def prime_factors(n: int) -> list[int]:
    """Return the prime factors of ``n`` in non-decreasing order."""
    return stats.prime_factors(n)


@mcp.tool()
def log_base(x: float, base: float) -> float:
    """Compute the logarithm of ``x`` with a custom ``base``."""
    return utils.log_base(x, base)


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise ``base`` to the given ``exponent``."""
    return utils.power(base, exponent)


@mcp.tool()
def to_scientific_notation(x: float, precision: int = 3) -> str:
    """Format a number in scientific notation with configurable precision."""
    return utils.to_scientific_notation(x, precision)


@mcp.tool()
def to_binary(n: int) -> str:
    """Convert an integer to its binary string representation."""
    return utils.to_binary(n)


@mcp.tool()
def from_binary(bin_str: str) -> int:
    """Convert a binary string to an integer."""
    return utils.from_binary(bin_str)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8080)
