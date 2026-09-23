from enum import Enum
from pydantic import BaseModel, Field


class BatchItemStatus(str, Enum):
    """
    Execution outcome for one requirement in a batch.

    PASS, REVIEW, and FAIL are V&V quality outcomes.

    ERROR means the requirement could not be completely
    processed because of a technical or input-processing
    failure.
    """

    PASS = "pass"
    REVIEW = "review"
    FAIL = "fail"
    ERROR = "error"


class BatchRequirementResult(BaseModel):
    """
    Summary of one requirement processed during a batch run.
    """

    requirement_id: str
    title: str | None = None

    status: BatchItemStatus

    input_file: str

    output_directory: str | None = None
    json_output: str | None = None
    review_report: str | None = None
    traceability_matrix: str | None = None

    feature_files: list[str] = Field(
        default_factory=list
    )

    requirement_coverage_percent: float = 0.0
    acceptance_criteria_coverage_percent: float = 0.0
    acceptance_criteria_accountability_percent: float = 0.0

    acceptance_criteria_count: int = 0

    testable_ac_count: int = 0
    limited_ac_count: int = 0
    blocked_ac_count: int = 0

    finding_count: int = 0

    master_scenario_count: int = 0
    jama_test_case_count: int = 0
    bdd_feature_count: int = 0
    bdd_scenario_count: int = 0

    jama_validation_status: str | None = None
    bdd_validation_status: str | None = None

    error_type: str | None = None
    error_message: str | None = None


class BatchSummary(BaseModel):
    """
    Aggregate deterministic summary for a complete batch run.
    """

    run_id: str

    total_requirements: int = 0
    successfully_processed: int = 0
    processing_errors: int = 0

    pass_count: int = 0
    review_count: int = 0
    fail_count: int = 0

    total_acceptance_criteria: int = 0

    total_testable_acs: int = 0
    total_limited_acs: int = 0
    total_blocked_acs: int = 0

    total_findings: int = 0

    total_master_scenarios: int = 0
    total_jama_test_cases: int = 0
    total_bdd_features: int = 0
    total_bdd_scenarios: int = 0

    average_requirement_coverage_percent: float = 0.0
    average_ac_coverage_percent: float = 0.0
    average_ac_accountability_percent: float = 0.0

    jama_validation_failures: int = 0
    bdd_validation_failures: int = 0

    results: list[BatchRequirementResult] = Field(
        default_factory=list
    )