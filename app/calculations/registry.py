from __future__ import annotations

from app.calculations.catalog import ALL_CALCULATIONS
from app.calculations.models import CalculationDefinition


class CalculationRegistry:
    """Zentrale Registry für benannte Berechnungen."""

    def __init__(self, definitions: tuple[CalculationDefinition, ...] = ()) -> None:
        self._definitions: dict[str, CalculationDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: CalculationDefinition) -> None:
        self._definitions[definition.id] = definition

    def list_calculations(self) -> list[CalculationDefinition]:
        return list(self._definitions.values())

    def get(self, calculation_id: str) -> CalculationDefinition | None:
        return self._definitions.get(calculation_id)


def get_registry() -> CalculationRegistry:
    """Factory für die Standard-Registry mit Katalogeinträgen."""

    return CalculationRegistry(definitions=ALL_CALCULATIONS)
