from __future__ import annotations

from app.calculations.registry import get_registry
from app.execution.calculation_executor import CalculationExecutor


def execute_calculation_tool(
    calculation_id: str,
    inputs: dict[str, object],
    executor: CalculationExecutor | None = None,
) -> dict[str, object]:
    active_executor = executor or CalculationExecutor(get_registry())
    return active_executor.execute_calculation(calculation_id, inputs)
