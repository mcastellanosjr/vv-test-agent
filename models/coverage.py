from pydantic import BaseModel, Field


class RequirementCoverage(BaseModel):
    requirement_id: str
    scenario_ids: list[str] = Field(default_factory=list)
    covered: bool


class AcceptanceCriterionCoverage(BaseModel):
    acceptance_criterion_id: str
    scenario_ids: list[str] = Field(default_factory=list)

    disposition: str | None = None

    covered: bool

    accounted_for: bool = False

    executable: bool = False


class CoverageAnalysis(BaseModel):
    requirement_coverage: list[
        RequirementCoverage
    ] = Field(default_factory=list)

    acceptance_criteria_coverage: list[
        AcceptanceCriterionCoverage
    ] = Field(default_factory=list)

    uncovered_requirement_ids: list[str] = Field(
        default_factory=list
    )

    uncovered_acceptance_criteria_ids: list[str] = Field(
        default_factory=list
    )

    unaccounted_acceptance_criteria_ids: list[str] = Field(
        default_factory=list
    )

    blocked_acceptance_criteria_ids: list[str] = Field(
        default_factory=list
    )

    orphan_scenario_ids: list[str] = Field(
        default_factory=list
    )

    invalid_requirement_references: list[str] = Field(
        default_factory=list
    )

    invalid_acceptance_criteria_references: list[str] = Field(
        default_factory=list
    )

    duplicate_scenario_ids: list[str] = Field(
        default_factory=list
    )

    requirement_coverage_percent: float = 0.0

    acceptance_criteria_coverage_percent: float = 0.0

    acceptance_criteria_accountability_percent: float = 0.0