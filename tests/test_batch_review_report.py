from models.batch import (
    BatchItemStatus,
    BatchRequirementResult,
    BatchSummary,
)
from renderers.batch_review_report_renderer import (
    render_batch_review_report,
    write_batch_review_report,
)


def create_test_summary():
    results = [
        BatchRequirementResult(
            requirement_id="REQ-001",
            title="Session Timeout",
            status=BatchItemStatus.REVIEW,
            input_file="REQ-001.json",
            output_directory="output/REQ-001",
            requirement_coverage_percent=100.0,
            acceptance_criteria_coverage_percent=100.0,
            acceptance_criteria_accountability_percent=100.0,
            acceptance_criteria_count=3,
            limited_ac_count=3,
            finding_count=2,
            master_scenario_count=3,
            jama_test_case_count=2,
            bdd_feature_count=1,
            bdd_scenario_count=3,
            jama_validation_status="pass",
            bdd_validation_status="pass",
        ),
        BatchRequirementResult(
            requirement_id="REQ-002",
            title="Name Length",
            status=BatchItemStatus.PASS,
            input_file="REQ-002.json",
            output_directory="output/REQ-002",
            requirement_coverage_percent=100.0,
            acceptance_criteria_coverage_percent=100.0,
            acceptance_criteria_accountability_percent=100.0,
            acceptance_criteria_count=2,
            testable_ac_count=2,
            master_scenario_count=2,
            jama_test_case_count=1,
            bdd_feature_count=1,
            bdd_scenario_count=2,
            jama_validation_status="pass",
            bdd_validation_status="pass",
        ),
        BatchRequirementResult(
            requirement_id="REQ-003",
            status=BatchItemStatus.ERROR,
            input_file="REQ-003.json",
            error_type="JSONDecodeError",
            error_message="Invalid JSON input.",
        ),
    ]

    return BatchSummary(
        run_id="test-run",
        total_requirements=3,
        successfully_processed=2,
        processing_errors=1,
        pass_count=1,
        review_count=1,
        fail_count=0,
        total_acceptance_criteria=5,
        total_testable_acs=2,
        total_limited_acs=3,
        total_blocked_acs=0,
        total_findings=2,
        total_master_scenarios=5,
        total_jama_test_cases=3,
        total_bdd_features=2,
        total_bdd_scenarios=5,
        average_requirement_coverage_percent=100.0,
        average_ac_coverage_percent=100.0,
        average_ac_accountability_percent=100.0,
        jama_validation_failures=0,
        bdd_validation_failures=0,
        results=results,
    )


def test_render_batch_review_report():
    summary = create_test_summary()

    report = render_batch_review_report(
        summary
    )

    assert "V&V BATCH REVIEW REPORT" in report
    assert "Run ID: test-run" in report

    assert (
        "Requirements Submitted:       3"
        in report
    )

    assert (
        "Successfully Processed:       2"
        in report
    )

    assert (
        "Processing Errors:            1"
        in report
    )

    assert "Requirement: REQ-001" in report
    assert "Requirement: REQ-002" in report
    assert "Requirement: REQ-003" in report

    assert "Status: REVIEW" in report
    assert "Status: PASS" in report
    assert "Status: ERROR" in report

    assert (
        "V&V Quality Determination: "
        "NOT PERFORMED"
        in report
    )

    assert (
        "Error Type: JSONDecodeError"
        in report
    )

    assert (
        "Requirements requiring V&V review: "
        "REQ-001"
        in report
    )

    assert (
        "Requirements failing quality gates: "
        "None"
        in report
    )

    assert (
        "Requirements with processing errors: "
        "REQ-003"
        in report
    )


def test_write_batch_review_report(
    tmp_path,
):
    summary = create_test_summary()

    output_path = write_batch_review_report(
        summary=summary,
        run_output_directory=tmp_path,
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "batch-review.txt"
    )

    content = output_path.read_text(
        encoding="utf-8"
    )

    assert "V&V BATCH REVIEW REPORT" in content
    assert "REQ-001" in content
    assert "REQ-003" in content