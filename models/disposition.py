from enum import Enum

from pydantic import BaseModel, Field


class VerificationDisposition(str, Enum):
    TESTABLE = "testable"
    LIMITED = "limited"
    BLOCKED = "blocked"


class AcceptanceCriterionDisposition(BaseModel):
    acceptance_criterion_id: str

    disposition: VerificationDisposition

    rationale: str

    supported_behavior: list[str] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )

    related_finding_ids: list[str] = Field(
        default_factory=list
    )


class DispositionCollection(BaseModel):
    dispositions: list[
        AcceptanceCriterionDisposition
    ] = Field(
        default_factory=list
    )