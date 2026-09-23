from pathlib import Path

from models.batch import (
    BatchItemStatus,
    BatchSummary,
)


def format_percent(value: float) -> str:
    return f"{value:.2f}%"


def join_requirement_ids(
    summary: BatchSummary,
    status: BatchItemStatus,
) -> str:
    requirement_ids = [
        result.requirement_id
        for result in summary.results
        if result.status == status
    ]

    if not requirement_ids:
        return "None"

    return ", ".join(requirement_ids)


def render_batch_review_report(
    summary: BatchSummary,
) -> str:
    """
    Render a deterministic human-readable V&V batch
    review report.

    No AI interpretation is performed in this renderer.
    """

    lines: list[str] = []

    lines.append(
        "V&V BATCH REVIEW REPORT"
    )
    lines.append(
        "=" * 72
    )
    lines.append("")

    # ---------------------------------------------------------
    # Run information
    # ---------------------------------------------------------

    lines.append(
        f"Run ID: {summary.run_id}"
    )
    lines.append("")

    # ---------------------------------------------------------
    # Overall batch status
    # ---------------------------------------------------------

    lines.append(
        "OVERALL BATCH STATUS"
    )
    lines.append(
        "-" * 72
    )

    lines.append(
        "Requirements Submitted:       "
        f"{summary.total_requirements}"
    )

    lines.append(
        "Successfully Processed:       "
        f"{summary.successfully_processed}"
    )

    lines.append(
        "Processing Errors:            "
        f"{summary.processing_errors}"
    )

    lines.append("")

    lines.append(
        "Quality Outcomes:"
    )

    lines.append(
        "  PASS:                       "
        f"{summary.pass_count}"
    )

    lines.append(
        "  REVIEW:                     "
        f"{summary.review_count}"
    )

    lines.append(
        "  FAIL:                       "
        f"{summary.fail_count}"
    )

    lines.append(
        "  ERROR:                      "
        f"{summary.processing_errors}"
    )

    lines.append("")

    # ---------------------------------------------------------
    # Verification disposition summary
    # ---------------------------------------------------------

    lines.append(
        "VERIFICATION DISPOSITION SUMMARY"
    )
    lines.append(
        "-" * 72
    )

    lines.append(
        "Total Acceptance Criteria:    "
        f"{summary.total_acceptance_criteria}"
    )

    lines.append(
        "TESTABLE:                     "
        f"{summary.total_testable_acs}"
    )

    lines.append(
        "LIMITED:                      "
        f"{summary.total_limited_acs}"
    )

    lines.append(
        "BLOCKED:                      "
        f"{summary.total_blocked_acs}"
    )

    lines.append("")

    # ---------------------------------------------------------
    # Generated verification design
    # ---------------------------------------------------------

    lines.append(
        "GENERATED VERIFICATION DESIGN"
    )
    lines.append(
        "-" * 72
    )

    lines.append(
        "Total Findings:               "
        f"{summary.total_findings}"
    )

    lines.append(
        "Master Test Scenarios:        "
        f"{summary.total_master_scenarios}"
    )

    lines.append(
        "JAMA Test Cases:              "
        f"{summary.total_jama_test_cases}"
    )

    lines.append(
        "BDD Features:                 "
        f"{summary.total_bdd_features}"
    )

    lines.append(
        "BDD Scenarios:                "
        f"{summary.total_bdd_scenarios}"
    )

    lines.append("")

    # ---------------------------------------------------------
    # Traceability health
    # ---------------------------------------------------------

    lines.append(
        "TRACEABILITY HEALTH"
    )
    lines.append(
        "-" * 72
    )

    lines.append(
        "Average Requirement Coverage: "
        f"{format_percent(summary.average_requirement_coverage_percent)}"
    )

    lines.append(
        "Average AC Executable Coverage: "
        f"{format_percent(summary.average_ac_coverage_percent)}"
    )

    lines.append(
        "Average AC Accountability:    "
        f"{format_percent(summary.average_ac_accountability_percent)}"
    )

    lines.append("")

    # ---------------------------------------------------------
    # Artifact validation
    # ---------------------------------------------------------

    lines.append(
        "ARTIFACT VALIDATION"
    )
    lines.append(
        "-" * 72
    )

    lines.append(
        "JAMA Validation Failures:     "
        f"{summary.jama_validation_failures}"
    )

    lines.append(
        "BDD Validation Failures:      "
        f"{summary.bdd_validation_failures}"
    )

    lines.append("")

    # ---------------------------------------------------------
    # Requirement-level results
    # ---------------------------------------------------------

    lines.append(
        "REQUIREMENT RESULTS"
    )
    lines.append(
        "-" * 72
    )

    if not summary.results:
        lines.append(
            "No requirements were processed."
        )

    for result in summary.results:
        lines.append("")

        lines.append(
            f"Requirement: {result.requirement_id}"
        )

        if result.title:
            lines.append(
                f"Title: {result.title}"
            )

        lines.append(
            "Status: "
            f"{result.status.value.upper()}"
        )

        lines.append(
            f"Input File: {result.input_file}"
        )

        if result.status == BatchItemStatus.ERROR:
            lines.append(
                "V&V Quality Determination: "
                "NOT PERFORMED"
            )

            lines.append(
                "Error Type: "
                f"{result.error_type or 'Unknown'}"
            )

            lines.append(
                "Error Message: "
                f"{result.error_message or 'No error message available.'}"
            )

            continue

        lines.append(
            "Requirement Coverage: "
            f"{format_percent(result.requirement_coverage_percent)}"
        )

        lines.append(
            "AC Executable Coverage: "
            f"{format_percent(result.acceptance_criteria_coverage_percent)}"
        )

        lines.append(
            "AC Accountability: "
            f"{format_percent(result.acceptance_criteria_accountability_percent)}"
        )

        lines.append(
            "Acceptance Criteria: "
            f"{result.acceptance_criteria_count}"
        )

        lines.append(
            "  TESTABLE: "
            f"{result.testable_ac_count}"
        )

        lines.append(
            "  LIMITED: "
            f"{result.limited_ac_count}"
        )

        lines.append(
            "  BLOCKED: "
            f"{result.blocked_ac_count}"
        )

        lines.append(
            "Findings: "
            f"{result.finding_count}"
        )

        lines.append(
            "Master Scenarios: "
            f"{result.master_scenario_count}"
        )

        lines.append(
            "JAMA Test Cases: "
            f"{result.jama_test_case_count}"
        )

        lines.append(
            "BDD Features: "
            f"{result.bdd_feature_count}"
        )

        lines.append(
            "BDD Scenarios: "
            f"{result.bdd_scenario_count}"
        )

        lines.append(
            "JAMA Validation: "
            f"{result.jama_validation_status or 'unknown'}"
        )

        lines.append(
            "BDD Validation: "
            f"{result.bdd_validation_status or 'unknown'}"
        )

        if result.output_directory:
            lines.append(
                "Output Directory: "
                f"{result.output_directory}"
            )

    lines.append("")
    lines.append("")

    # ---------------------------------------------------------
    # Human review priorities
    # ---------------------------------------------------------

    lines.append(
        "HUMAN REVIEW PRIORITIES"
    )
    lines.append(
        "-" * 72
    )

    lines.append(
        "Requirements requiring V&V review: "
        + join_requirement_ids(
            summary,
            BatchItemStatus.REVIEW,
        )
    )

    lines.append(
        "Requirements failing quality gates: "
        + join_requirement_ids(
            summary,
            BatchItemStatus.FAIL,
        )
    )

    lines.append(
        "Requirements with processing errors: "
        + join_requirement_ids(
            summary,
            BatchItemStatus.ERROR,
        )
    )

    lines.append("")

    lines.append(
        "NOTE: ERROR indicates that processing did not "
        "complete and therefore no V&V quality "
        "determination was made for that requirement."
    )

    lines.append(
        "PASS, REVIEW, and FAIL are V&V quality outcomes "
        "for requirements that completed processing."
    )

    lines.append("")

    return "\n".join(lines)


def write_batch_review_report(
    summary: BatchSummary,
    run_output_directory: Path,
) -> Path:
    """
    Write the deterministic batch review report.
    """

    run_output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        run_output_directory
        / "batch-review.txt"
    )

    output_path.write_text(
        render_batch_review_report(summary),
        encoding="utf-8",
    )

    return output_path