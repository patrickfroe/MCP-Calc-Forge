from __future__ import annotations

import ast

from app.validation.errors import FieldError


class ExpressionValidator:
    """Validiert mathematische Expressions gegen eine sichere AST-Whitelist."""

    _ALLOWED_BINARY_OPERATORS = (ast.Add, ast.Sub, ast.Mult, ast.Div)
    _ALLOWED_UNARY_OPERATORS = (ast.UAdd, ast.USub)

    def validate(self, expression: str) -> tuple[FieldError, ...]:
        if not isinstance(expression, str) or not expression.strip():
            return (
                FieldError(
                    field="expression",
                    code="invalid_expression",
                    message="Expression muss ein nicht-leerer String sein.",
                ),
            )

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError:
            return (
                FieldError(
                    field="expression",
                    code="invalid_expression",
                    message="Expression enthält ungültige Syntax.",
                ),
            )

        errors = self._validate_node(tree)
        return tuple(errors)

    def _validate_node(self, node: ast.AST) -> list[FieldError]:
        if isinstance(node, ast.Expression):
            return self._validate_node(node.body)

        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, self._ALLOWED_BINARY_OPERATORS):
                return [self._unsupported_syntax_error(node)]
            return self._validate_node(node.left) + self._validate_node(node.right)

        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, self._ALLOWED_UNARY_OPERATORS):
                return [self._unsupported_syntax_error(node)]
            return self._validate_node(node.operand)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return []
            return [self._unsupported_syntax_error(node)]

        if isinstance(node, ast.Name):
            return [
                FieldError(
                    field="expression",
                    code="unsafe_expression",
                    message="Namen sind in Expressions nicht erlaubt.",
                    received=node.id,
                )
            ]

        if isinstance(node, ast.Call):
            return [
                FieldError(
                    field="expression",
                    code="unsafe_expression",
                    message="Funktionsaufrufe sind in Expressions nicht erlaubt.",
                )
            ]

        if isinstance(node, ast.Attribute):
            return [
                FieldError(
                    field="expression",
                    code="unsafe_expression",
                    message="Attribute sind in Expressions nicht erlaubt.",
                )
            ]

        return [self._unsupported_syntax_error(node)]

    @staticmethod
    def _unsupported_syntax_error(node: ast.AST) -> FieldError:
        return FieldError(
            field="expression",
            code="unsafe_expression",
            message="Nicht erlaubte Syntax in Expression.",
            received=type(node).__name__,
        )
