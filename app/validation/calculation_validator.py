from __future__ import annotations

from app.calculations.models import CalculationDefinition, InputField
from app.validation.errors import FieldError


class CalculationValidator:
    """Validiert Input-Payloads gegen die Felddefinitionen einer Berechnung."""

    _TYPE_MAP = {
        "number": (int, float),
        "integer": (int,),
        "string": (str,),
        "boolean": (bool,),
        "number_list": (list,),
    }

    def validate(self, definition: CalculationDefinition, payload: dict[str, object]) -> tuple[FieldError, ...]:
        errors: list[FieldError] = []
        for field in definition.input_fields:
            errors.extend(self._validate_field(field, payload))
        return tuple(errors)

    def _validate_field(self, field: InputField, payload: dict[str, object]) -> list[FieldError]:
        if field.name not in payload:
            if field.required:
                return [
                    FieldError(
                        field=field.name,
                        code="required",
                        message=f"Pflichtfeld '{field.name}' fehlt.",
                    )
                ]
            return []

        value = payload[field.name]
        expected_types = self._TYPE_MAP.get(field.field_type)
        if expected_types is None:
            return [
                FieldError(
                    field=field.name,
                    code="unsupported_type",
                    message=f"Nicht unterstützter Feldtyp '{field.field_type}'.",
                )
            ]

        if isinstance(value, bool) and field.field_type in {"number", "integer"}:
            return [
                FieldError(
                    field=field.name,
                    code="invalid_type",
                    message=f"Feld '{field.name}' muss Typ {field.field_type} haben.",
                    expected=field.field_type,
                    received=type(value).__name__,
                )
            ]

        if not isinstance(value, expected_types):
            return [
                FieldError(
                    field=field.name,
                    code="invalid_type",
                    message=f"Feld '{field.name}' muss Typ {field.field_type} haben.",
                    expected=field.field_type,
                    received=type(value).__name__,
                )
            ]

        list_error = self._validate_number_list(field, value)
        if list_error:
            return [list_error]

        range_error = self._validate_range(field, value)
        if range_error:
            return [range_error]

        enum_error = self._validate_enum(field, value)
        if enum_error:
            return [enum_error]

        return []

    @staticmethod
    def _validate_number_list(field: InputField, value: object) -> FieldError | None:
        if field.field_type != "number_list":
            return None

        if not isinstance(value, list):
            return FieldError(
                field=field.name,
                code="invalid_type",
                message=f"Feld '{field.name}' muss Typ number_list haben.",
                expected="number_list",
                received=type(value).__name__,
            )

        if not value:
            return FieldError(
                field=field.name,
                code="invalid_value",
                message=f"Feld '{field.name}' darf keine leere Liste sein.",
            )

        if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
            return FieldError(
                field=field.name,
                code="invalid_type",
                message=f"Feld '{field.name}' muss nur numerische Werte enthalten.",
                expected="list[number]",
            )

        return None

    @staticmethod
    def _validate_range(field: InputField, value: object) -> FieldError | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None

        if field.min_value is not None and value < field.min_value:
            return FieldError(
                field=field.name,
                code="out_of_range",
                message=f"Feld '{field.name}' muss >= {field.min_value} sein.",
                expected=f">= {field.min_value}",
                received=value,
            )

        if field.max_value is not None and value > field.max_value:
            return FieldError(
                field=field.name,
                code="out_of_range",
                message=f"Feld '{field.name}' muss <= {field.max_value} sein.",
                expected=f"<= {field.max_value}",
                received=value,
            )

        return None

    @staticmethod
    def _validate_enum(field: InputField, value: object) -> FieldError | None:
        if field.allowed_values and value not in field.allowed_values:
            return FieldError(
                field=field.name,
                code="invalid_enum",
                message=f"Feld '{field.name}' hat keinen erlaubten Enum-Wert.",
                expected=str(list(field.allowed_values)),
                received=value,
            )
        return None
