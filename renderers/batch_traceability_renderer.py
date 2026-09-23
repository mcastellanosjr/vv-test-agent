import csv
from pathlib import Path

from models.batch import (
    BatchItemStatus,
    BatchSummary,
)


BATCH_TRACEABILITY_COLUMNS = [
    "requirement_id",
    "requirement_title",
    "requirement_status",
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


def read_requirement_traceability(
    traceability_path: Path,
    requirement_status: str,
) -> list[dict[str, str]]:
    """
    Read one requirement-level traceability CSV and
    add the requirement's batch quality status.
    """

    rows: list[dict[str, str]] = []

    with traceability_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for source_row in reader:
            row = {
                column: ""
                for column
                in BATCH_TRACEABILITY_COLUMNS
            }

            for column in (
                BATCH_TRACEABILITY_COLUMNS
            ):
                if (
                    column
                    == "requirement_status"
                ):
                    continue

                row[column] = (
                    source_row.get(
                        column,
                        "",
                    )
                    or ""
                )

            row[
                "requirement_status"
            ] = requirement_status

            rows.append(row)

    return rows


def create_error_traceability_row(
    requirement_id: str,
    requirement_title: str | None,
) -> dict[str, str]:
    """
    Preserve a batch-level traceability row for a
    requirement that could not complete processing.

    No verification traceability is invented.
    """

    row = {
        column: ""
        for column
        in BATCH_TRACEABILITY_COLUMNS
    }

    row["requirement_id"] = (
        requirement_id
    )

    row["requirement_title"] = (
        requirement_title or ""
    )

    row["requirement_status"] = (
        BatchItemStatus.ERROR.value
    )

    row["executable_coverage"] = (
        "not_performed"
    )

    row["accounted_for"] = (
        "not_performed"
    )

    return row


def collect_batch_traceability_rows(
    summary: BatchSummary,
) -> list[dict[str, str]]:
    """
    Collect requirement-level traceability into one
    deterministic batch-level row collection.
    """

    rows: list[dict[str, str]] = []

    for result in summary.results:
        if (
            result.status
            == BatchItemStatus.ERROR
        ):
            rows.append(
                create_error_traceability_row(
                    requirement_id=(
                        result.requirement_id
                    ),
                    requirement_title=(
                        result.title
                    ),
                )
            )

            continue

        if not result.traceability_matrix:
            # Successfully processed requirement but
            # traceability artifact is unexpectedly absent.
            # Preserve visibility without inventing mappings.
            row = {
                column: ""
                for column
                in BATCH_TRACEABILITY_COLUMNS
            }

            row["requirement_id"] = (
                result.requirement_id
            )

            row["requirement_title"] = (
                result.title or ""
            )

            row["requirement_status"] = (
                result.status.value
            )

            row["executable_coverage"] = (
                "traceability_missing"
            )

            row["accounted_for"] = (
                "traceability_missing"
            )

            rows.append(row)

            continue

        traceability_path = Path(
            result.traceability_matrix
        )

        if not traceability_path.exists():
            row = {
                column: ""
                for column
                in BATCH_TRACEABILITY_COLUMNS
            }

            row["requirement_id"] = (
                result.requirement_id
            )

            row["requirement_title"] = (
                result.title or ""
            )

            row["requirement_status"] = (
                result.status.value
            )

            row["executable_coverage"] = (
                "traceability_missing"
            )

            row["accounted_for"] = (
                "traceability_missing"
            )

            rows.append(row)

            continue

        rows.extend(
            read_requirement_traceability(
                traceability_path=(
                    traceability_path
                ),
                requirement_status=(
                    result.status.value
                ),
            )
        )

    return rows


def write_batch_traceability_matrix(
    summary: BatchSummary,
    run_output_directory: Path,
) -> Path:
    """
    Write one consolidated traceability CSV for the
    complete batch run.
    """

    run_output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        run_output_directory
        / "batch-traceability.csv"
    )

    rows = (
        collect_batch_traceability_rows(
            summary
        )
    )

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                BATCH_TRACEABILITY_COLUMNS
            ),
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return output_path