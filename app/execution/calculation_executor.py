from __future__ import annotations

from app.calculations.registry import CalculationRegistry
from app.validation.calculation_validator import CalculationValidator
from app.validation.errors import FieldError, error_response


class CalculationExecutor:
    """Führt benannte Berechnungen aus, inklusive vorgeschalteter Validierung."""

    def __init__(self, registry: CalculationRegistry, validator: CalculationValidator | None = None) -> None:
        self._registry = registry
        self._validator = validator or CalculationValidator()

    def execute_calculation(self, calculation_id: str, payload: dict[str, object]) -> dict[str, object]:
        definition = self._registry.get(calculation_id)
        if definition is None:
            return error_response(
                code="UNKNOWN_CALCULATION_ID",
                message=f"Unbekannte calculation_id '{calculation_id}'.",
            )

        validation_errors = self._validator.validate(definition, payload)
        if validation_errors:
            return error_response(
                code="VALIDATION_ERROR",
                message="Validierung fehlgeschlagen.",
                details=validation_errors,
            )

        try:
            result = definition.execute(payload)
        except ValueError as error:
            return error_response(
                code="VALIDATION_ERROR",
                message="Validierung fehlgeschlagen.",
                details=(
                    FieldError(
                        field="payload",
                        code="invalid_value",
                        message=str(error),
                    ),
                ),
            )

        return {"ok": True, "calculation_id": definition.id, "result": result}
