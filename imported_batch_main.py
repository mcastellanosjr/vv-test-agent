from pathlib import Path

from agent.batch_runner import run_batch
from renderers.batch_review_report_renderer import (
    write_batch_review_report,
)
from renderers.batch_traceability_renderer import (
    write_batch_traceability_matrix,
)


INPUT_DIRECTORY = Path(
    "input/staged_requirements"
)

OUTPUT_ROOT = Path(
    "output"
)

DEFAULT_PROJECT = "ActiveConnect"


def validate_staged_input(
    input_directory: Path,
) -> list[Path]:
    """
    Verify that the staged input directory exists and
    contains at least one JSON requirement file.

    Returns the staged JSON files in deterministic order.
    """

    if not input_directory.exists():
        raise RuntimeError(
            "Staged requirement directory does "
            "not exist. Run import_requirements.py "
            "before imported batch processing."
        )

    if not input_directory.is_dir():
        raise RuntimeError(
            "Staged requirement input path is "
            "not a directory."
        )

    requirement_files = sorted(
        path
        for path in input_directory.glob(
            "*.json"
        )
        if path.is_file()
    )

    if not requirement_files:
        raise RuntimeError(
            "No staged requirement JSON files "
            "were found. Run import_requirements.py "
            "before imported batch processing."
        )

    return requirement_files


def main():
    print()
    print(
        "========================================"
    )
    print(
        " V&V IMPORTED REQUIREMENT BATCH"
    )
    print(
        "========================================"
    )
    print()

    requirement_files = (
        validate_staged_input(
            INPUT_DIRECTORY
        )
    )

    print(
        f"Input Directory: "
        f"{INPUT_DIRECTORY}"
    )

    print(
        "Staged Requirements: "
        f"{len(requirement_files)}"
    )

    print()

    for requirement_file in (
        requirement_files
    ):
        print(
            f"- {requirement_file.name}"
        )

    print()

    # ---------------------------------------------------------
    # Existing stable batch engine
    # ---------------------------------------------------------

    summary, summary_file = run_batch(
        input_directory=INPUT_DIRECTORY,
        output_root=OUTPUT_ROOT,
        project=DEFAULT_PROJECT,
    )

    run_output_directory = (
        summary_file.parent
    )

    # ---------------------------------------------------------
    # Batch-level deterministic artifacts
    # ---------------------------------------------------------

    batch_review_report = (
        write_batch_review_report(
            summary=summary,
            run_output_directory=(
                run_output_directory
            ),
        )
    )

    batch_traceability = (
        write_batch_traceability_matrix(
            summary=summary,
            run_output_directory=(
                run_output_directory
            ),
        )
    )

    # ---------------------------------------------------------
    # Console summary
    # ---------------------------------------------------------

    print()
    print(
        "========================================"
    )
    print(
        " IMPORTED BATCH SUMMARY"
    )
    print(
        "========================================"
    )

    print(
        f"Run ID:                      "
        f"{summary.run_id}"
    )

    print(
        f"Requirements Submitted:      "
        f"{summary.total_requirements}"
    )

    print(
        f"Successfully Processed:      "
        f"{summary.successfully_processed}"
    )

    print(
        f"Processing Errors:           "
        f"{summary.processing_errors}"
    )

    print()

    print(
        f"PASS:                        "
        f"{summary.pass_count}"
    )

    print(
        f"REVIEW:                      "
        f"{summary.review_count}"
    )

    print(
        f"FAIL:                        "
        f"{summary.fail_count}"
    )

    print()

    print(
        f"Total Acceptance Criteria:   "
        f"{summary.total_acceptance_criteria}"
    )

    print(
        f"TESTABLE ACs:                "
        f"{summary.total_testable_acs}"
    )

    print(
        f"LIMITED ACs:                 "
        f"{summary.total_limited_acs}"
    )

    print(
        f"BLOCKED ACs:                 "
        f"{summary.total_blocked_acs}"
    )

    print()

    print(
        f"Master Scenarios:            "
        f"{summary.total_master_scenarios}"
    )

    print(
        f"JAMA Test Cases:             "
        f"{summary.total_jama_test_cases}"
    )

    print(
        f"BDD Features:                "
        f"{summary.total_bdd_features}"
    )

    print(
        f"BDD Scenarios:               "
        f"{summary.total_bdd_scenarios}"
    )

    print()

    print(
        "Avg Requirement Coverage:    "
        f"{summary.average_requirement_coverage_percent:.1f}%"
    )

    print(
        "Avg AC Executable Coverage:  "
        f"{summary.average_ac_coverage_percent:.1f}%"
    )

    print(
        "Avg AC Accountability:       "
        f"{summary.average_ac_accountability_percent:.1f}%"
    )

    print()

    print(
        "PER-REQUIREMENT RESULTS"
    )

    print(
        "-" * 72
    )

    for result in summary.results:
        print(
            f"{result.requirement_id}: "
            f"{result.status.value.upper()}"
        )

        if result.error_type:
            print(
                f"  Error Type: "
                f"{result.error_type}"
            )

            print(
                f"  Error: "
                f"{result.error_message}"
            )

            continue

        print(
            "  Requirement Coverage: "
            f"{result.requirement_coverage_percent:.1f}%"
        )

        print(
            "  AC Executable Coverage: "
            f"{result.acceptance_criteria_coverage_percent:.1f}%"
        )

        print(
            "  AC Accountability: "
            f"{result.acceptance_criteria_accountability_percent:.1f}%"
        )

        print(
            "  JAMA Validation: "
            f"{result.jama_validation_status}"
        )

        print(
            "  BDD Validation: "
            f"{result.bdd_validation_status}"
        )

    print()

    print(
        f"Batch Summary:       "
        f"{summary_file}"
    )

    print(
        f"Batch Review Report: "
        f"{batch_review_report}"
    )

    print(
        f"Batch Traceability:  "
        f"{batch_traceability}"
    )

    print()


if __name__ == "__main__":
    main()