import json

from agent.batch_runner import (
    build_batch_summary,
    calculate_average,
    discover_requirement_files,
)
from models.batch import (
    BatchItemStatus,
    BatchRequirementResult,
)


def test_discover_requirement_files(tmp_path):
    (tmp_path / "REQ-002.json").write_text(
        "{}",
        encoding="utf-8",
    )

    (tmp_path / "REQ-001.json").write_text(
        "{}",
        encoding="utf-8",
    )

    (tmp_path / "notes.txt").write_text(
        "ignore",
        encoding="utf-8",
    )

    files = discover_requirement_files(
        tmp_path
    )

    assert [
        file.name
        for file in files
    ] == [
        "REQ-001.json",
        "REQ-002.json",
    ]


def test_calculate_average():
    assert calculate_average(
        [100.0, 50.0, 75.0]
    ) == 75.0

    assert calculate_average([]) == 0.0


def test_build_batch_summary():
    results = [
        BatchRequirementResult(
            requirement_id="REQ-001",
            status=BatchItemStatus.PASS,
            input_file="REQ-001.json",
            acceptance_criteria_count=3,
            testable_ac_count=2,
            limited_ac_count=1,
            finding_count=1,
            master_scenario_count=3,
            jama_test_case_count=2,
            bdd_feature_count=1,
            bdd_scenario_count=3,
            requirement_coverage_percent=100.0,
            acceptance_criteria_coverage_percent=100.0,
            acceptance_criteria_accountability_percent=100.0,
            jama_validation_status="pass",
            bdd_validation_status="pass",
        ),
        BatchRequirementResult(
            requirement_id="REQ-002",
            status=BatchItemStatus.REVIEW,
            input_file="REQ-002.json",
            acceptance_criteria_count=2,
            limited_ac_count=2,
            finding_count=2,
            master_scenario_count=2,
            jama_test_case_count=1,
            bdd_feature_count=1,
            bdd_scenario_count=2,
            requirement_coverage_percent=100.0,
            acceptance_criteria_coverage_percent=50.0,
            acceptance_criteria_accountability_percent=100.0,
            jama_validation_status="pass",
            bdd_validation_status="pass",
        ),
        BatchRequirementResult(
            requirement_id="REQ-003",
            status=BatchItemStatus.ERROR,
            input_file="REQ-003.json",
            error_type="RuntimeError",
            error_message="Processing failed.",
        ),
    ]

    summary = build_batch_summary(
        run_id="test-run",
        results=results,
    )

    assert summary.total_requirements == 3
    assert summary.successfully_processed == 2
    assert summary.processing_errors == 1

    assert summary.pass_count == 1
    assert summary.review_count == 1
    assert summary.fail_count == 0

    assert (
        summary.total_acceptance_criteria
        == 5
    )

    assert summary.total_testable_acs == 2
    assert summary.total_limited_acs == 3
    assert summary.total_blocked_acs == 0

    assert summary.total_findings == 3
    assert summary.total_master_scenarios == 5
    assert summary.total_jama_test_cases == 3
    assert summary.total_bdd_features == 2
    assert summary.total_bdd_scenarios == 5

    assert (
        summary.average_requirement_coverage_percent
        == 100.0
    )

    assert (
        summary.average_ac_coverage_percent
        == 75.0
    )

    assert (
        summary.average_ac_accountability_percent
        == 100.0
    )

    assert summary.jama_validation_failures == 0
    assert summary.bdd_validation_failures == 0


def test_error_result_does_not_affect_averages():
    results = [
        BatchRequirementResult(
            requirement_id="REQ-001",
            status=BatchItemStatus.PASS,
            input_file="REQ-001.json",
            requirement_coverage_percent=100.0,
            acceptance_criteria_coverage_percent=100.0,
            acceptance_criteria_accountability_percent=100.0,
        ),
        BatchRequirementResult(
            requirement_id="REQ-002",
            status=BatchItemStatus.ERROR,
            input_file="REQ-002.json",
            error_type="JSONDecodeError",
            error_message="Invalid JSON.",
        ),
    ]

    summary = build_batch_summary(
        run_id="test-run",
        results=results,
    )

    assert (
        summary.average_requirement_coverage_percent
        == 100.0
    )

    assert (
        summary.average_ac_coverage_percent
        == 100.0
    )

    assert (
        summary.average_ac_accountability_percent
        == 100.0
    )