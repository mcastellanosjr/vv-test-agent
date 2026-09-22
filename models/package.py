from enum import Enum

from pydantic import BaseModel, Field

from models.analysis import RequirementAnalysis
from models.bdd import BDDFeature
from models.coverage import CoverageAnalysis
from models.disposition import AcceptanceCriterionDisposition
from models.finding import AnalysisFinding
from models.grouping import ScenarioGrouping
from models.jama import JamaTestCase
from models.quality import QualityGateResult
from models.requirement import Requirement
from models.scenario import TestScenario


class ReviewStatus(str, Enum):
    READY = "ready"
    REVIEW_RECOMMENDED = "review_recommended"
    BLOCKED = "blocked"


class VVDesignPackageV1(BaseModel):
    project: str

    requirement: Requirement

    analysis: RequirementAnalysis

    findings: list[AnalysisFinding] = Field(
        default_factory=list
    )

    review_status: ReviewStatus

    verification_dispositions: list[
        AcceptanceCriterionDisposition
    ] = Field(
        default_factory=list
    )

    disposition_validation: dict = Field(
        default_factory=dict
    )

    test_scenarios: list[TestScenario] = Field(
        default_factory=list
    )

    coverage: CoverageAnalysis

    scenario_grouping: ScenarioGrouping

    jama_test_cases: list[JamaTestCase] = Field(
        default_factory=list
    )

    jama_validation: dict = Field(
        default_factory=dict
    )

    bdd_features: list[BDDFeature] = Field(
        default_factory=list
    )

    bdd_validation: dict = Field(
        default_factory=dict
    )

    quality_gate: QualityGateResult