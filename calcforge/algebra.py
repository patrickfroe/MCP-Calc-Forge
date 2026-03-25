"""Algebra utilities for MCP CalcForge.

This module provides symbolic helpers for solving equations,
factoring polynomials, and finding roots via SymPy.
"""

from __future__ import annotations

from sympy import Eq, factor, linsolve, solve, symbols, sympify


def solve_quadratic(a: float, b: float, c: float) -> tuple:
    """Solve ``a*x**2 + b*x + c = 0`` and return both roots.

    Args:
        a: Quadratic coefficient of ``x**2``.
        b: Linear coefficient of ``x``.
        c: Constant term.

    Returns:
        A tuple with two real or complex solutions.

    Raises:
        ValueError: If ``a`` is zero.
    """
    if a == 0:
        raise ValueError("Parameter 'a' must be non-zero for a quadratic equation.")

    x = symbols("x")
    solutions = solve(a * x**2 + b * x + c, x)
    return tuple(solutions)


def solve_linear_system(equations: list[str], variables: list[str]) -> dict:
    """Solve a linear system using :func:`sympy.linsolve`.

    Args:
        equations: Linear equations as strings, e.g. ``"2*x + y = 5"``.
        variables: Variable names, e.g. ``["x", "y"]``.

    Returns:
        A mapping of variable name to solved value. Returns an empty dict
        if no solution exists.
    """
    symbol_map = {name: symbols(name) for name in variables}
    parsed_equations = []

    for equation in equations:
        if "=" in equation:
            left, right = equation.split("=", 1)
            parsed_equations.append(Eq(sympify(left, locals=symbol_map), sympify(right, locals=symbol_map)))
        else:
            parsed_equations.append(sympify(equation, locals=symbol_map))

    solution_set = linsolve(parsed_equations, *[symbol_map[name] for name in variables])
    if not solution_set:
        return {}

    solution_tuple = next(iter(solution_set))
    return {name: value for name, value in zip(variables, solution_tuple)}


def factor_polynomial(expr: str) -> str:
    """Factor a polynomial expression and return it as a string."""
    return str(factor(sympify(expr)))


def find_roots(expr: str) -> list:
    """Find polynomial roots for a univariate expression.

    Args:
        expr: Polynomial expression string, e.g. ``"x**2 - 4"``.

    Returns:
        A list of roots (real or complex).

    Raises:
        ValueError: If the expression is not univariate.
    """
    parsed_expr = sympify(expr)
    free_symbols = sorted(parsed_expr.free_symbols, key=lambda sym: sym.name)

    if not free_symbols:
        return []
    if len(free_symbols) > 1:
        raise ValueError("Expression must be univariate to find roots.")

    return list(solve(parsed_expr, free_symbols[0]))
