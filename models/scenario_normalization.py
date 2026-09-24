from enum import Enum

from pydantic import BaseModel, Field

from models.scenario import TestScenario


class ScenarioNormalizationStatus(
    str,
    Enum,
):
    ACCEPTED = "accepted"
    LIMITED = "limited"
    REJECTED = "rejected"


class ScenarioNormalizationRecord(
    BaseModel
):
    """
    Records what happened to one supplied scenario during
    normalization.
    """

    source_scenario_id: str

    status: ScenarioNormalizationStatus

    normalized_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    rationale: str

    limitations: list[str] = Field(
        default_factory=list
    )


class ScenarioNormalizationResult(
    BaseModel
):
    """
    Complete result of normalizing supplied scenarios into
    canonical master scenarios.
    """

    normalized_scenarios: list[
        TestScenario
    ] = Field(
        default_factory=list
    )

    records: list[
        ScenarioNormalizationRecord
    ] = Field(
        default_factory=list
    )