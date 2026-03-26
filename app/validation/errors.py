from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldError:
    field: str
    code: str
    message: str
    expected: str | None = None
    received: Any = None


@dataclass(frozen=True)
class ErrorModel:
    code: str
    message: str
    details: tuple[FieldError, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": [asdict(detail) for detail in self.details],
        }


def error_response(code: str, message: str, details: tuple[FieldError, ...] = ()) -> dict[str, Any]:
    return {"ok": False, "error": ErrorModel(code=code, message=message, details=details).to_dict()}
