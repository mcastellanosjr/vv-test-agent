from enum import Enum

from pydantic import BaseModel, Field


class SuppliedScenarioSource(str, Enum):
    MANUAL = "manual"
    CSV = "csv"
    JAMA = "jama"
    FILE = "file"
    OTHER = "other"


class SuppliedTestScenario(BaseModel):
    """
    Test scenario supplied as source material.

    This model preserves the scenario as provided before
    any AI interpretation or normalization occurs.
    """

    source_scenario_id: str

    title: str

    description: str | None = None

    preconditions: list[str] = Field(
        default_factory=list
    )

    actions: list[str] = Field(
        default_factory=list
    )

    expected_results: list[str] = Field(
        default_factory=list
    )

    requirement_ids: list[str] = Field(
        default_factory=list
    )

    acceptance_criteria_ids: list[str] = Field(
        default_factory=list
    )

    source: SuppliedScenarioSource = (
        SuppliedScenarioSource.MANUAL
    )

    source_reference: str | None = None


class SuppliedScenarioCollection(BaseModel):
    scenarios: list[
        SuppliedTestScenario
    ] = Field(
        default_factory=list
    )