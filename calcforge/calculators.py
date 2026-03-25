"""Calculator registry and workflows for MCP CalcForge.

All calculators were intentionally removed from this service.
"""

from __future__ import annotations

from typing import Any


def _error_response(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def list_calculators(category: str | None = None) -> list[dict[str, Any]]:
    """List available calculator metadata.

    This always returns an empty list because no calculators are registered.
    """
    return []


def get_calculator_schema(slug: str) -> dict[str, Any]:
    """Return a JSON error because calculator schemas are unavailable."""
    return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})


def calculate(slug: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON error because no calculators are available."""
    return _error_response("unknown_slug", f"Unknown calculator slug: {slug}", {"slug": slug})
