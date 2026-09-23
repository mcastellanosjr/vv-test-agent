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

from unittest.mock import patch

from agent.batch_runner import (
    process_requirement_file,
)
from models.batch import BatchItemStatus


def write_valid_requirement(
    file_path,
    requirement_id,
):
    file_path.write_text(
        json.dumps(
            {
                "project": "ActiveConnect",
                "requirement": {
                    "requirement_id": requirement_id,
                    "title": "Test Requirement",
                    "text": (
                        "The system shall perform "
                        "the specified behavior."
                    ),
                    "acceptance_criteria": [
                        {
                            "id": "AC-01",
                            "text": (
                                "The specified behavior "
                                "is observable."
                            ),
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )


def test_pipeline_failure_becomes_error_result(
    tmp_path,
):
    input_file = (
        tmp_path / "REQ-ERROR.json"
    )

    write_valid_requirement(
        input_file,
        "REQ-ERROR",
    )

    run_output_directory = (
        tmp_path / "output"
    )

    with patch(
        "agent.batch_runner.run_pipeline",
        side_effect=RuntimeError(
            "Cursor execution failed."
        ),
    ):
        result = process_requirement_file(
            input_file=input_file,
            project="ActiveConnect",
            run_output_directory=(
                run_output_directory
            ),
        )

    assert (
        result.status
        == BatchItemStatus.ERROR
    )

    assert (
        result.requirement_id
        == "REQ-ERROR"
    )

    assert (
        result.error_type
        == "RuntimeError"
    )

    assert (
        result.error_message
        == "Cursor execution failed."
    )


def test_processing_can_continue_after_pipeline_failure(
    tmp_path,
):
    first_file = (
        tmp_path / "REQ-001.json"
    )

    second_file = (
        tmp_path / "REQ-002.json"
    )

    write_valid_requirement(
        first_file,
        "REQ-001",
    )

    write_valid_requirement(
        second_file,
        "REQ-002",
    )

    run_output_directory = (
        tmp_path / "output"
    )

    call_count = 0

    def simulated_pipeline(
        project,
        requirement,
    ):
        nonlocal call_count
        call_count += 1

        if (
            requirement.requirement_id
            == "REQ-001"
        ):
            raise RuntimeError(
                "Simulated Cursor failure."
            )

        raise RuntimeError(
            "Second requirement reached."
        )

    with patch(
        "agent.batch_runner.run_pipeline",
        side_effect=simulated_pipeline,
    ):
        first_result = (
            process_requirement_file(
                input_file=first_file,
                project="ActiveConnect",
                run_output_directory=(
                    run_output_directory
                ),
            )
        )

        second_result = (
            process_requirement_file(
                input_file=second_file,
                project="ActiveConnect",
                run_output_directory=(
                    run_output_directory
                ),
            )
        )

    assert call_count == 2

    assert (
        first_result.status
        == BatchItemStatus.ERROR
    )

    assert (
        first_result.error_message
        == "Simulated Cursor failure."
    )

    assert (
        second_result.status
        == BatchItemStatus.ERROR
    )

    assert (
        second_result.error_message
        == "Second requirement reached."
    )