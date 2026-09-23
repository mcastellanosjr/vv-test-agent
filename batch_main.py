from pathlib import Path

from agent.batch_runner import run_batch
from models.batch import BatchItemStatus

from renderers.batch_review_report_renderer import (
    write_batch_review_report,
)

from renderers.batch_traceability_renderer import (
    write_batch_traceability_matrix,
)

INPUT_DIRECTORY = Path(
    "input/requirements"
)

OUTPUT_ROOT = Path(
    "output"
)

DEFAULT_PROJECT = "ActiveConnect"


def main():
    print()
    print(
        "========================================"
    )
    print(
        " V&V TEST DESIGN AGENT - BATCH MODE"
    )
    print(
        "========================================"
    )
    print()

    # ---------------------------------------------------------
    # Verify input directory
    # ---------------------------------------------------------

    if not INPUT_DIRECTORY.exists():
        raise FileNotFoundError(
            "Batch input directory not found: "
            f"{INPUT_DIRECTORY}"
        )

    # ---------------------------------------------------------
    # Execute batch
    # ---------------------------------------------------------

    summary, summary_file = run_batch(
        input_directory=INPUT_DIRECTORY,
        output_root=OUTPUT_ROOT,
        project=DEFAULT_PROJECT,
    )

    run_output_directory = (
    summary_file.parent
    )

    batch_review_report = (
        write_batch_review_report(
            summary=summary,
            run_output_directory=run_output_directory,
        )
    )

    batch_traceability = (
    write_batch_traceability_matrix(
        summary=summary,
        run_output_directory=run_output_directory,
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
        " BATCH EXECUTION COMPLETE"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Run ID: {summary.run_id}"
    )

    print()

    print(
        "Requirements Submitted:       "
        f"{summary.total_requirements}"
    )

    print(
        "Successfully Processed:       "
        f"{summary.successfully_processed}"
    )

    print(
        "Processing Errors:            "
        f"{summary.processing_errors}"
    )

    print()

    print(
        "PASS:                         "
        f"{summary.pass_count}"
    )

    print(
        "REVIEW:                       "
        f"{summary.review_count}"
    )

    print(
        "FAIL:                         "
        f"{summary.fail_count}"
    )

    print()

    print(
        "Total Acceptance Criteria:    "
        f"{summary.total_acceptance_criteria}"
    )

    print(
        "TESTABLE ACs:                 "
        f"{summary.total_testable_acs}"
    )

    print(
        "LIMITED ACs:                  "
        f"{summary.total_limited_acs}"
    )

    print(
        "BLOCKED ACs:                  "
        f"{summary.total_blocked_acs}"
    )

    print()

    print(
        "Total Findings:               "
        f"{summary.total_findings}"
    )

    print(
        "Master Scenarios:             "
        f"{summary.total_master_scenarios}"
    )

    print(
        "JAMA Test Cases:              "
        f"{summary.total_jama_test_cases}"
    )

    print(
        "BDD Features:                 "
        f"{summary.total_bdd_features}"
    )

    print(
        "BDD Scenarios:                "
        f"{summary.total_bdd_scenarios}"
    )

    print()

    print(
        "Avg Requirement Coverage:     "
        f"{summary.average_requirement_coverage_percent:.2f}%"
    )

    print(
        "Avg AC Executable Coverage:   "
        f"{summary.average_ac_coverage_percent:.2f}%"
    )

    print(
        "Avg AC Accountability:        "
        f"{summary.average_ac_accountability_percent:.2f}%"
    )

    print()

    print(
        "JAMA Validation Failures:     "
        f"{summary.jama_validation_failures}"
    )

    print(
        "BDD Validation Failures:      "
        f"{summary.bdd_validation_failures}"
    )

    # ---------------------------------------------------------
    # Requirement-level results
    # ---------------------------------------------------------

    if summary.results:
        print()
        print(
            "----------------------------------------"
        )
        print(
            " REQUIREMENT RESULTS"
        )
        print(
            "----------------------------------------"
        )

        for result in summary.results:
            print()

            print(
                f"{result.requirement_id}: "
                f"{result.status.value.upper()}"
            )

            if result.title:
                print(
                    f"  Title: {result.title}"
                )

            if (
                result.status
                == BatchItemStatus.ERROR
            ):
                print(
                    "  Error Type: "
                    f"{result.error_type}"
                )

                print(
                    "  Error: "
                    f"{result.error_message}"
                )

            else:
                print(
                    "  AC Coverage: "
                    f"{result.acceptance_criteria_coverage_percent:.2f}%"
                )

                print(
                    "  AC Accountability: "
                    f"{result.acceptance_criteria_accountability_percent:.2f}%"
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
        "----------------------------------------"
    )

    print(
        "Batch Summary: "
        f"{summary_file}"
    )

    print(
        "Batch Review Report: "
        f"{batch_review_report}"
    )

    print(
        "Batch Traceability: "
        f"{batch_traceability}"
    )

    print(
        "----------------------------------------"
    )

    print()


if __name__ == "__main__":
    main()