from __future__ import annotations

import ast
import math

from app.validation.errors import error_response
from app.validation.expression_validator import ExpressionValidator


class ExpressionEngine:
    """Sichere Auswertung mathematischer Expressions ohne eval()."""

    def __init__(self, validator: ExpressionValidator | None = None) -> None:
        self._validator = validator or ExpressionValidator()

    def evaluate(self, expression: str) -> dict[str, object]:
        validation_errors = self._validator.validate(expression)
        if validation_errors:
            return error_response(
                code="INVALID_EXPRESSION",
                message="Expression ist ungültig oder unsicher.",
                details=validation_errors,
            )

        tree = ast.parse(expression, mode="eval")
        try:
            value = self._evaluate_node(tree.body)
        except ZeroDivisionError:
            return error_response(
                code="INVALID_EXPRESSION",
                message="Division durch 0 ist nicht erlaubt.",
            )

        if not math.isfinite(value):
            return error_response(
                code="INVALID_EXPRESSION",
                message="Expression ergibt keinen endlichen numerischen Wert.",
            )

        return {"ok": True, "result": {"value": value}}

    def _evaluate_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            return float(node.value)

        if isinstance(node, ast.UnaryOp):
            operand = self._evaluate_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operand
            if isinstance(node.op, ast.USub):
                return -operand

        if isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right

        raise ValueError(f"Unexpected AST node: {type(node).__name__}")
