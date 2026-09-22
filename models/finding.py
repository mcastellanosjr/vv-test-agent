from enum import Enum

from pydantic import BaseModel, Field


class FindingType(str, Enum):
    AMBIGUITY = "ambiguity"
    MISSING_INFORMATION = "missing_information"
    CONTRADICTION = "contradiction"
    UNTESTABLE = "untestable"
    ASSUMPTION = "assumption"


class FindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisFinding(BaseModel):

    id: str

    finding_type: FindingType

    severity: FindingSeverity

    source_reference: str | None = None

    description: str

    impact: str

    clarification_question: str | None = None

class FindingCollection(BaseModel):
    findings: list[AnalysisFinding] = Field(default_factory=list)