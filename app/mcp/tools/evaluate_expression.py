from __future__ import annotations

from app.execution.expression_engine import ExpressionEngine


def evaluate_expression_tool(
    expression: str,
    engine: ExpressionEngine | None = None,
) -> dict[str, object]:
    active_engine = engine or ExpressionEngine()
    return active_engine.evaluate(expression)
