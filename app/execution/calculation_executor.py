from __future__ import annotations

from app.calculations.registry import CalculationRegistry
from app.validation.calculation_validator import CalculationValidator
from app.validation.errors import error_response


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

        result = self._run(definition.id, payload)
        return {"ok": True, "calculation_id": definition.id, "result": result}

    def _run(self, calculation_id: str, payload: dict[str, object]) -> dict[str, float]:
        if calculation_id == "percentage_of":
            part = float(payload["part"])
            whole = float(payload["whole"])
            return {"percentage": (part / whole) * 100}

        if calculation_id == "vat_add":
            net_amount = float(payload["net_amount"])
            vat_rate = float(payload["vat_rate"])
            gross_amount = net_amount * (1 + (vat_rate / 100))
            return {"gross_amount": gross_amount, "vat_amount": gross_amount - net_amount}

        if calculation_id == "simple_interest":
            principal = float(payload["principal"])
            annual_rate = float(payload["annual_rate"])
            years = float(payload["years"])
            interest = principal * (annual_rate / 100) * years
            return {"interest": interest, "total_amount": principal + interest}

        return {"unsupported": 0.0}
