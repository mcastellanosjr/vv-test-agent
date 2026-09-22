from agent.quality_gate import evaluate_quality_gate
from models.coverage import CoverageAnalysis
from models.finding import (
    AnalysisFinding,
    FindingSeverity,
    FindingType,
)
from models.quality import QualityGateStatus


def clean_coverage():
    return CoverageAnalysis(
        uncovered_requirement_ids=[],
        uncovered_acceptance_criteria_ids=[],
        unaccounted_acceptance_criteria_ids=[],
        blocked_acceptance_criteria_ids=[],
        orphan_scenario_ids=[],
        invalid_requirement_references=[],
        invalid_acceptance_criteria_references=[],
        duplicate_scenario_ids=[],
        requirement_coverage_percent=100.0,
        acceptance_criteria_coverage_percent=100.0,
        acceptance_criteria_accountability_percent=100.0,
    )


def passing_validation():
    return {
        "status": "pass",
        "valid": True,
        "errors": [],
    }


def test_clean_package_passes():
    result = evaluate_quality_gate(
        coverage=clean_coverage(),
        findings=[],
        jama_validation=passing_validation(),
        bdd_validation=passing_validation(),
    )

    assert (
        result.status
        == QualityGateStatus.PASS
    )

    assert result.blocking_reasons == []


def test_medium_finding_requires_review():
    finding = AnalysisFinding(
        id="FIND-001",
        finding_type=FindingType.AMBIGUITY,
        severity=FindingSeverity.MEDIUM,
        description="Timing tolerance is undefined.",
        impact="Verification precision is limited.",
    )

    result = evaluate_quality_gate(
        coverage=clean_coverage(),
        findings=[finding],
        jama_validation=passing_validation(),
        bdd_validation=passing_validation(),
    )

    assert (
        result.status
        == QualityGateStatus.REVIEW
    )

    assert result.medium_findings == 1


def test_uncovered_nonblocked_ac_fails():
    coverage = clean_coverage()

    coverage.uncovered_acceptance_criteria_ids = [
        "AC-02"
    ]

    result = evaluate_quality_gate(
        coverage=coverage,
        findings=[],
        jama_validation=passing_validation(),
        bdd_validation=passing_validation(),
    )

    assert (
        result.status
        == QualityGateStatus.FAIL
    )

    assert result.blocking_reasons


def test_blocked_ac_requires_review_not_failure():
    coverage = clean_coverage()

    coverage.uncovered_acceptance_criteria_ids = [
        "AC-02"
    ]

    coverage.blocked_acceptance_criteria_ids = [
        "AC-02"
    ]

    coverage.acceptance_criteria_coverage_percent = (
        66.67
    )

    result = evaluate_quality_gate(
        coverage=coverage,
        findings=[],
        jama_validation=passing_validation(),
        bdd_validation=passing_validation(),
    )

    assert (
        result.status
        == QualityGateStatus.REVIEW
    )

    assert result.blocking_reasons == []


def test_jama_failure_fails_quality_gate():
    jama_validation = {
        "status": "fail",
        "valid": False,
        "errors": [
            "Traceability failure."
        ],
    }

    result = evaluate_quality_gate(
        coverage=clean_coverage(),
        findings=[],
        jama_validation=jama_validation,
        bdd_validation=passing_validation(),
    )

    assert (
        result.status
        == QualityGateStatus.FAIL
    )


def test_not_run_downstream_fails_quality_gate():
    not_run = {
        "status": "not_run",
        "valid": None,
        "errors": [],
        "reason": "Upstream gate failed.",
    }

    result = evaluate_quality_gate(
        coverage=clean_coverage(),
        findings=[],
        jama_validation=not_run,
        bdd_validation=not_run,
    )

    assert (
        result.status
        == QualityGateStatus.FAIL
    )

    assert result.blocking_reasons