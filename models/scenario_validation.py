from enum import Enum

from pydantic import BaseModel, Field


class ScenarioValidationSeverity(
    str,
    Enum,
):
    ERROR = "error"
    WARNING = "warning"


class ScenarioValidationIssue(
    BaseModel
):
    source_scenario_id: str | None = None
    severity: ScenarioValidationSeverity
    field: str | None = None
    message: str


class SuppliedScenarioValidationResult(
    BaseModel
):
    valid: bool

    errors: list[
        ScenarioValidationIssue
    ] = Field(
        default_factory=list
    )

    warnings: list[
        ScenarioValidationIssue
    ] = Field(
        default_factory=list
    )

    scenario_count: int = 0
    valid_scenario_count: int = 0
    invalid_scenario_count: int = 0