from enum import Enum

from pydantic import BaseModel, Field


class QualityGateStatus(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    FAIL = "fail"


class QualityGateResult(BaseModel):
    status: QualityGateStatus

    blocking_reasons: list[str] = Field(
        default_factory=list
    )

    review_reasons: list[str] = Field(
        default_factory=list
    )

    requirement_coverage_percent: float = 0.0
    acceptance_criteria_coverage_percent: float = 0.0

    jama_valid: bool = False
    bdd_valid: bool = False

    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    info_findings: int = 0