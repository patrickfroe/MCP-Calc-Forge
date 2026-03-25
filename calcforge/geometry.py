"""Geometry utilities for MCP CalcForge.

This module provides common area, perimeter, circumference, and volume
calculations for basic geometric shapes.
"""

from __future__ import annotations

import math


def circle_area(radius: float) -> float:
    """Calculate the area of a circle using ``πr²``.

    Args:
        radius: Circle radius.

    Returns:
        The circle area.
    """
    return math.pi * radius**2


def circle_circumference(radius: float) -> float:
    """Calculate the circumference of a circle using ``2πr``.

    Args:
        radius: Circle radius.

    Returns:
        The circle circumference.
    """
    return 2 * math.pi * radius


def rectangle_area(a: float, b: float) -> float:
    """Calculate the area of a rectangle.

    Args:
        a: Length of the first side.
        b: Length of the second side.

    Returns:
        The rectangle area.
    """
    return a * b


def rectangle_perimeter(a: float, b: float) -> float:
    """Calculate the perimeter of a rectangle.

    Args:
        a: Length of the first side.
        b: Length of the second side.

    Returns:
        The rectangle perimeter.
    """
    return 2 * (a + b)


def triangle_area(base: float, height: float) -> float:
    """Calculate the area of a triangle using ``½ * base * height``.

    Args:
        base: Triangle base length.
        height: Triangle height.

    Returns:
        The triangle area.
    """
    return 0.5 * base * height


def sphere_volume(radius: float) -> float:
    """Calculate the volume of a sphere using ``4/3 * π * r³``.

    Args:
        radius: Sphere radius.

    Returns:
        The sphere volume.
    """
    return (4.0 / 3.0) * math.pi * radius**3


def cylinder_volume(radius: float, height: float) -> float:
    """Calculate the volume of a cylinder using ``π * r² * h``.

    Args:
        radius: Cylinder radius.
        height: Cylinder height.

    Returns:
        The cylinder volume.
    """
    return math.pi * radius**2 * height


def cone_volume(radius: float, height: float) -> float:
    """Calculate the volume of a cone using ``1/3 * π * r² * h``.

    Args:
        radius: Cone base radius.
        height: Cone height.

    Returns:
        The cone volume.
    """
    return (1.0 / 3.0) * math.pi * radius**2 * height


def pyramid_volume(base_area: float, height: float) -> float:
    """Calculate the volume of a pyramid using ``1/3 * base_area * height``.

    Args:
        base_area: Pyramid base area.
        height: Pyramid height.

    Returns:
        The pyramid volume.
    """
    return (1.0 / 3.0) * base_area * height
