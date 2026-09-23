from models.batch import (
    BatchItemStatus,
    BatchRequirementResult,
    BatchSummary,
)


def test_batch_requirement_result():
    result = BatchRequirementResult(
        requirement_id="REQ-001",
        title="Session Timeout",
        status=BatchItemStatus.REVIEW,
        input_file="REQ-001.json",
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
    )

    assert result.requirement_id == "REQ-001"
    assert result.title == "Session Timeout"
    assert result.status == BatchItemStatus.REVIEW

    assert (
        result.requirement_coverage_percent
        == 100.0
    )

    assert (
        result.acceptance_criteria_coverage_percent
        == 100.0
    )

    assert (
        result.acceptance_criteria_accountability_percent
        == 100.0
    )

    assert result.acceptance_criteria_count == 3
    assert result.limited_ac_count == 3

    assert result.finding_count == 2

    assert result.master_scenario_count == 3
    assert result.jama_test_case_count == 2
    assert result.bdd_feature_count == 1
    assert result.bdd_scenario_count == 3

    assert result.jama_validation_status == "pass"
    assert result.bdd_validation_status == "pass"

    assert result.error_type is None
    assert result.error_message is None


def test_error_result():
    result = BatchRequirementResult(
        requirement_id="UNKNOWN",
        status=BatchItemStatus.ERROR,
        input_file="invalid.json",
        error_type="JSONDecodeError",
        error_message="Invalid JSON input.",
    )

    assert result.status == BatchItemStatus.ERROR
    assert result.error_type == "JSONDecodeError"
    assert result.error_message == "Invalid JSON input."

    assert result.output_directory is None
    assert result.json_output is None
    assert result.review_report is None
    assert result.traceability_matrix is None

    assert result.feature_files == []


def test_batch_summary():
    results = [
        BatchRequirementResult(
            requirement_id="REQ-001",
            status=BatchItemStatus.PASS,
            input_file="REQ-001.json",
        ),
        BatchRequirementResult(
            requirement_id="REQ-002",
            status=BatchItemStatus.REVIEW,
            input_file="REQ-002.json",
        ),
        BatchRequirementResult(
            requirement_id="REQ-003",
            status=BatchItemStatus.ERROR,
            input_file="REQ-003.json",
            error_type="RuntimeError",
            error_message="Processing failed.",
        ),
    ]

    summary = BatchSummary(
        run_id="test-run",
        total_requirements=3,
        successfully_processed=2,
        processing_errors=1,
        pass_count=1,
        review_count=1,
        fail_count=0,
        results=results,
    )

    assert summary.run_id == "test-run"

    assert summary.total_requirements == 3
    assert summary.successfully_processed == 2
    assert summary.processing_errors == 1

    assert summary.pass_count == 1
    assert summary.review_count == 1
    assert summary.fail_count == 0

    assert len(summary.results) == 3

    assert (
        summary.results[0].status
        == BatchItemStatus.PASS
    )

    assert (
        summary.results[1].status
        == BatchItemStatus.REVIEW
    )

    assert (
        summary.results[2].status
        == BatchItemStatus.ERROR
    )

    assert (
        summary.results[2].error_type
        == "RuntimeError"
    )