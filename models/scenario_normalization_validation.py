from pydantic import BaseModel, Field


class ScenarioNormalizationValidationResult(
    BaseModel
):
    valid: bool

    errors: list[str] = Field(
        default_factory=list
    )

    missing_source_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    unknown_source_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    duplicate_source_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    duplicate_normalized_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    unknown_normalized_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    unmapped_accepted_or_limited_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    mapped_rejected_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )

    invalid_requirement_references: list[
        str
    ] = Field(
        default_factory=list
    )

    invalid_acceptance_criteria_references: list[
        str
    ] = Field(
        default_factory=list
    )

    orphan_normalized_scenario_ids: list[
        str
    ] = Field(
        default_factory=list
    )