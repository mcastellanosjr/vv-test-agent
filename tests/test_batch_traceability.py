import csv

from models.batch import (
    BatchItemStatus,
    BatchRequirementResult,
    BatchSummary,
)
from renderers.batch_traceability_renderer import (
    collect_batch_traceability_rows,
    write_batch_traceability_matrix,
)


def create_requirement_traceability(
    path,
):
    columns = [
        "requirement_id",
        "requirement_title",
        "acceptance_criterion_id",
        "acceptance_criterion",
        "disposition",
        "disposition_rationale",
        "finding_ids",
        "finding_severities",
        "master_scenario_id",
        "master_scenario_title",
        "master_test_type",
        "jama_test_case_ids",
        "jama_test_case_names",
        "bdd_feature_ids",
        "bdd_feature_names",
        "bdd_scenario_ids",
        "bdd_scenario_names",
        "executable_coverage",
        "accounted_for",
    ]

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )

        writer.writeheader()

        writer.writerow(
            {
                "requirement_id": "REQ-001",
                "requirement_title": "Session Timeout",
                "acceptance_criterion_id": "AC-01",
                "acceptance_criterion": "Warning displayed.",
                "disposition": "limited",
                "disposition_rationale": "Timing behavior is testable.",
                "finding_ids": "F-001",
                "finding_severities": "medium",
                "master_scenario_id": "TS-001",
                "master_scenario_title": "Display warning",
                "master_test_type": "state_transition",
                "jama_test_case_ids": "TC-001",
                "jama_test_case_names": "Session timeout warning",
                "bdd_feature_ids": "FEAT-001",
                "bdd_feature_names": "Session Timeout",
                "bdd_scenario_ids": "BDD-001",
                "bdd_scenario_names": "Display timeout warning",
                "executable_coverage": "True",
                "accounted_for": "True",
            }
        )


def test_collect_batch_traceability_rows(
    tmp_path,
):
    traceability_file = (
        tmp_path / "REQ-001-traceability.csv"
    )

    create_requirement_traceability(
        traceability_file
    )

    summary = BatchSummary(
        run_id="test-run",
        total_requirements=2,
        successfully_processed=1,
        processing_errors=1,
        review_count=1,
        results=[
            BatchRequirementResult(
                requirement_id="REQ-001",
                title="Session Timeout",
                status=BatchItemStatus.REVIEW,
                input_file="REQ-001.json",
                traceability_matrix=str(
                    traceability_file
                ),
            ),
            BatchRequirementResult(
                requirement_id="REQ-002",
                title="Invalid Requirement",
                status=BatchItemStatus.ERROR,
                input_file="REQ-002.json",
                error_type="JSONDecodeError",
                error_message="Invalid JSON.",
            ),
        ],
    )

    rows = (
        collect_batch_traceability_rows(
            summary
        )
    )

    assert len(rows) == 2

    assert (
        rows[0]["requirement_id"]
        == "REQ-001"
    )

    assert (
        rows[0]["requirement_status"]
        == "review"
    )

    assert (
        rows[0]["acceptance_criterion_id"]
        == "AC-01"
    )

    assert (
        rows[0]["master_scenario_id"]
        == "TS-001"
    )

    assert (
        rows[0]["jama_test_case_ids"]
        == "TC-001"
    )

    assert (
        rows[0]["bdd_scenario_ids"]
        == "BDD-001"
    )

    assert (
        rows[1]["requirement_id"]
        == "REQ-002"
    )

    assert (
        rows[1]["requirement_status"]
        == "error"
    )

    assert (
        rows[1]["executable_coverage"]
        == "not_performed"
    )

    assert (
        rows[1]["accounted_for"]
        == "not_performed"
    )


def test_write_batch_traceability_matrix(
    tmp_path,
):
    traceability_file = (
        tmp_path / "REQ-001-traceability.csv"
    )

    create_requirement_traceability(
        traceability_file
    )

    summary = BatchSummary(
        run_id="test-run",
        total_requirements=1,
        successfully_processed=1,
        review_count=1,
        results=[
            BatchRequirementResult(
                requirement_id="REQ-001",
                title="Session Timeout",
                status=BatchItemStatus.REVIEW,
                input_file="REQ-001.json",
                traceability_matrix=str(
                    traceability_file
                ),
            )
        ],
    )

    output_path = (
        write_batch_traceability_matrix(
            summary=summary,
            run_output_directory=tmp_path,
        )
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "batch-traceability.csv"
    )

    with output_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 1

    assert (
        rows[0]["requirement_id"]
        == "REQ-001"
    )

    assert (
        rows[0]["requirement_status"]
        == "review"
    )

    assert (
        rows[0]["acceptance_criterion_id"]
        == "AC-01"
    )