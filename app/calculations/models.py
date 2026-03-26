from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class InputField:
    """Beschreibt ein einzelnes Eingabefeld einer Berechnung."""

    name: str
    field_type: str
    description: str
    required: bool = True
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CalculationExample:
    """Beispiel für die Verwendung einer Berechnung."""

    title: str
    input: dict[str, Any]


@dataclass(frozen=True)
class CalculationDefinition:
    """Metadaten und Ausführungslogik einer registrierten Berechnung."""

    id: str
    name: str
    description: str
    llm_usage_hint: str
    input_fields: tuple[InputField, ...]
    output_description: str
    output_type: str
    examples: tuple[CalculationExample, ...]
    execute: Callable[[dict[str, object]], object]
