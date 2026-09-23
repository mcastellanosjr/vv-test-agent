from pathlib import Path

from importers.csv_requirement_importer import (
    import_requirements_csv,
)
from importers.requirement_stager import (
    stage_import_result,
)


SOURCE_FILE = Path(
    "input/imports/requirements.csv"
)

STAGING_DIRECTORY = Path(
    "input/staged_requirements"
)


def print_import_findings(
    heading: str,
    findings,
):
    if not findings:
        return

    print()
    print(heading)
    print("-" * 72)

    for finding in findings:
        location_parts = []

        if finding.row_number is not None:
            location_parts.append(
                f"Row {finding.row_number}"
            )

        if finding.requirement_id:
            location_parts.append(
                f"Requirement "
                f"{finding.requirement_id}"
            )

        if finding.field:
            location_parts.append(
                f"Field {finding.field}"
            )

        if location_parts:
            location = " | ".join(
                location_parts
            )

            print(
                f"- {location}: "
                f"{finding.message}"
            )
        else:
            print(
                f"- {finding.message}"
            )


def clear_staging_directory(
    staging_directory: Path,
):
    """
    Remove previously staged JSON requirement files.

    Only JSON files directly inside the dedicated staging
    directory are removed. No other input folders are touched.
    """

    staging_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path in staging_directory.glob(
        "*.json"
    ):
        if path.is_file():
            path.unlink()


def main():
    print()
    print(
        "========================================"
    )
    print(
        " V&V REQUIREMENT CSV IMPORT"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Source: {SOURCE_FILE}"
    )

    print(
        f"Staging Directory: "
        f"{STAGING_DIRECTORY}"
    )

    print()

    # ---------------------------------------------------------
    # Import and validate entire CSV
    # ---------------------------------------------------------

    result = import_requirements_csv(
        SOURCE_FILE
    )

    print(
        "Rows Read:                   "
        f"{result.total_rows}"
    )

    print(
        "Requirements Normalized:     "
        f"{result.requirement_count}"
    )

    print(
        "Acceptance Criteria:         "
        f"{result.acceptance_criteria_count}"
    )

    print(
        "Warnings:                    "
        f"{len(result.warnings)}"
    )

    print(
        "Errors:                      "
        f"{len(result.errors)}"
    )

    # ---------------------------------------------------------
    # Show warnings
    # ---------------------------------------------------------

    print_import_findings(
        heading="IMPORT WARNINGS",
        findings=result.warnings,
    )

    # ---------------------------------------------------------
    # Block staging when validation errors exist
    # ---------------------------------------------------------

    if not result.valid:
        print_import_findings(
            heading="IMPORT ERRORS",
            findings=result.errors,
        )

        print()
        print(
            "IMPORT BLOCKED"
        )

        print(
            "No staged requirement files "
            "were created or replaced."
        )

        print(
            "Correct the CSV errors and "
            "run the import again."
        )

        print()

        return

    # ---------------------------------------------------------
    # Only clear old staging after the new import is valid.
    #
    # This means an invalid CSV cannot destroy the last
    # successfully staged requirement set.
    # ---------------------------------------------------------

    clear_staging_directory(
        STAGING_DIRECTORY
    )

    # ---------------------------------------------------------
    # Stage normalized JSON files
    # ---------------------------------------------------------

    staged_files = stage_import_result(
        import_result=result,
        output_directory=(
            STAGING_DIRECTORY
        ),
    )

    print()
    print(
        "IMPORT VALIDATION: PASS"
    )

    print()

    print(
        "STAGED REQUIREMENTS"
    )

    print(
        "-" * 72
    )

    for path in staged_files:
        print(
            f"- {path}"
        )

    print()

    print(
        "Requirements Staged:         "
        f"{len(staged_files)}"
    )

    print()

    print(
        "CSV import completed "
        "successfully."
    )

    print()


if __name__ == "__main__":
    main()