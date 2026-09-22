from models.coverage import CoverageAnalysis
from models.finding import (
    AnalysisFinding,
    FindingSeverity,
)
from models.quality import (
    QualityGateResult,
    QualityGateStatus,
)
from models.validation import ValidationStatus


def evaluate_quality_gate(
    coverage: CoverageAnalysis,
    findings: list[AnalysisFinding],
    jama_validation: dict,
    bdd_validation: dict,
) -> QualityGateResult:
    """
    Evaluate whether the generated V&V design package is
    structurally suitable for human review.

    PASS:
        Structurally complete with no material findings.

    REVIEW:
        Structurally complete, but findings require or
        recommend human V&V review.

    FAIL:
        Structural, traceability, or blocking verification
        problems prevent release of a complete package.
    """

    blocking_reasons = []
    review_reasons = []

    # ---------------------------------------------------------
    # Finding counts
    # ---------------------------------------------------------

    critical_findings = sum(
        1
        for finding in findings
        if finding.severity
        == FindingSeverity.CRITICAL
    )

    high_findings = sum(
        1
        for finding in findings
        if finding.severity
        == FindingSeverity.HIGH
    )

    medium_findings = sum(
        1
        for finding in findings
        if finding.severity
        == FindingSeverity.MEDIUM
    )

    low_findings = sum(
        1
        for finding in findings
        if finding.severity
        == FindingSeverity.LOW
    )

    info_findings = sum(
        1
        for finding in findings
        if finding.severity
        == FindingSeverity.INFO
    )

    # ---------------------------------------------------------
    # Critical findings
    # ---------------------------------------------------------

    if critical_findings:
        blocking_reasons.append(
            "One or more CRITICAL verification findings "
            "prevent meaningful verification."
        )

    # ---------------------------------------------------------
    # Requirement coverage
    # ---------------------------------------------------------

    if coverage.uncovered_requirement_ids:
        blocking_reasons.append(
            "One or more requirements have no master "
            "scenario coverage."
        )

    # ---------------------------------------------------------
    # AC accountability
    # ---------------------------------------------------------

    if coverage.unaccounted_acceptance_criteria_ids:
        blocking_reasons.append(
            "One or more acceptance criteria are not "
            "accounted for by a verification disposition."
        )

    # ---------------------------------------------------------
    # Non-blocked AC executable coverage
    # ---------------------------------------------------------

    non_blocked_uncovered_acs = [
        ac_id
        for ac_id
        in coverage.uncovered_acceptance_criteria_ids
        if ac_id
        not in coverage.blocked_acceptance_criteria_ids
    ]

    if non_blocked_uncovered_acs:
        blocking_reasons.append(
            "One or more TESTABLE or LIMITED acceptance "
            "criteria have no master scenario coverage."
        )

    # ---------------------------------------------------------
    # Blocked ACs
    # ---------------------------------------------------------

    if coverage.blocked_acceptance_criteria_ids:
        review_reasons.append(
            f"{len(coverage.blocked_acceptance_criteria_ids)} "
            "acceptance criterion/criteria are BLOCKED "
            "from executable verification."
        )

    # ---------------------------------------------------------
    # Master scenario structural integrity
    # ---------------------------------------------------------

    if coverage.orphan_scenario_ids:
        blocking_reasons.append(
            "One or more master scenarios are not traced "
            "to a requirement."
        )

    if coverage.invalid_requirement_references:
        blocking_reasons.append(
            "Invalid requirement references exist in "
            "master scenarios."
        )

    if coverage.invalid_acceptance_criteria_references:
        blocking_reasons.append(
            "Invalid acceptance criterion references "
            "exist in master scenarios."
        )

    if coverage.duplicate_scenario_ids:
        blocking_reasons.append(
            "Duplicate master scenario IDs exist."
        )

    # ---------------------------------------------------------
    # JAMA validation
    # ---------------------------------------------------------

    jama_status = jama_validation.get(
        "status"
    )

    jama_valid = (
        jama_status
        == ValidationStatus.PASS.value
    )

    if (
        jama_status
        == ValidationStatus.FAIL.value
    ):
        blocking_reasons.append(
            "JAMA traceability validation failed."
        )

    elif (
        jama_status
        == ValidationStatus.NOT_RUN.value
    ):
        blocking_reasons.append(
            "JAMA generation and validation were not run "
            "because an upstream verification gate failed."
        )

    # ---------------------------------------------------------
    # BDD validation
    # ---------------------------------------------------------

    bdd_status = bdd_validation.get(
        "status"
    )

    bdd_valid = (
        bdd_status
        == ValidationStatus.PASS.value
    )

    if (
        bdd_status
        == ValidationStatus.FAIL.value
    ):
        blocking_reasons.append(
            "BDD traceability validation failed."
        )

    elif (
        bdd_status
        == ValidationStatus.NOT_RUN.value
    ):
        blocking_reasons.append(
            "BDD generation and validation were not run "
            "because an upstream verification gate failed."
        )

    # ---------------------------------------------------------
    # Findings requiring review
    # ---------------------------------------------------------

    if high_findings:
        review_reasons.append(
            f"{high_findings} HIGH verification "
            "finding(s) require human review."
        )

    if medium_findings:
        review_reasons.append(
            f"{medium_findings} MEDIUM verification "
            "finding(s) require human review."
        )

    if low_findings:
        review_reasons.append(
            f"{low_findings} LOW verification "
            "finding(s) are present."
        )

    # ---------------------------------------------------------
    # Final status
    # ---------------------------------------------------------

    if blocking_reasons:
        status = QualityGateStatus.FAIL

    elif review_reasons:
        status = QualityGateStatus.REVIEW

    else:
        status = QualityGateStatus.PASS

    return QualityGateResult(
        status=status,
        blocking_reasons=blocking_reasons,
        review_reasons=review_reasons,
        requirement_coverage_percent=(
            coverage.requirement_coverage_percent
        ),
        acceptance_criteria_coverage_percent=(
            coverage.acceptance_criteria_coverage_percent
        ),
        jama_valid=jama_valid,
        bdd_valid=bdd_valid,
        critical_findings=critical_findings,
        high_findings=high_findings,
        medium_findings=medium_findings,
        low_findings=low_findings,
        info_findings=info_findings,
    )