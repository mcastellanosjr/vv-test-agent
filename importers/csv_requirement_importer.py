import csv
from pathlib import Path

from models.import_result import (
    ImportFinding,
    ImportedRequirement,
    RequirementImportResult,
)
from models.requirement import (
    AcceptanceCriterion,
    Requirement,
)


REQUIRED_COLUMNS = {
    "project",
    "requirement_id",
    "requirement_title",
    "requirement_text",
    "ac_id",
    "ac_text",
}


def clean(value: str | None) -> str:
    if value is None:
        return ""

    return value.strip()


def import_requirements_csv(
    source_file: Path,
) -> RequirementImportResult:
    """
    Import a CSV containing requirements and acceptance
    criteria into the agent's normalized Requirement model.

    One CSV row represents one acceptance criterion.
    Multiple rows with the same requirement_id are grouped
    into one Requirement.
    """

    result = RequirementImportResult(
        source_file=str(source_file)
    )

    if not source_file.exists():
        result.errors.append(
            ImportFinding(
                message=(
                    "CSV source file does not exist."
                )
            )
        )
        return result

    if not source_file.is_file():
        result.errors.append(
            ImportFinding(
                message=(
                    "CSV source path is not a file."
                )
            )
        )
        return result

    try:
        with source_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                result.errors.append(
                    ImportFinding(
                        message=(
                            "CSV file does not contain "
                            "a header row."
                        )
                    )
                )
                return result

            actual_columns = {
                clean(column)
                for column in reader.fieldnames
                if column is not None
            }

            missing_columns = (
                REQUIRED_COLUMNS
                - actual_columns
            )

            if missing_columns:
                result.errors.append(
                    ImportFinding(
                        message=(
                            "CSV is missing required "
                            "columns: "
                            + ", ".join(
                                sorted(
                                    missing_columns
                                )
                            )
                        )
                    )
                )
                return result

            grouped: dict[
                str,
                dict,
            ] = {}

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                result.total_rows += 1

                project = clean(
                    row.get("project")
                )

                requirement_id = clean(
                    row.get("requirement_id")
                )

                requirement_title = clean(
                    row.get(
                        "requirement_title"
                    )
                )

                requirement_text = clean(
                    row.get(
                        "requirement_text"
                    )
                )

                ac_id = clean(
                    row.get("ac_id")
                )

                ac_text = clean(
                    row.get("ac_text")
                )

                # ---------------------------------------------
                # Required row-level values
                # ---------------------------------------------

                required_values = {
                    "project": project,
                    "requirement_id": (
                        requirement_id
                    ),
                    "requirement_text": (
                        requirement_text
                    ),
                    "ac_id": ac_id,
                    "ac_text": ac_text,
                }

                row_has_error = False

                for (
                    field_name,
                    field_value,
                ) in required_values.items():
                    if field_value:
                        continue

                    result.errors.append(
                        ImportFinding(
                            row_number=(
                                row_number
                            ),
                            requirement_id=(
                                requirement_id
                                or None
                            ),
                            field=field_name,
                            message=(
                                f"Required field "
                                f"'{field_name}' "
                                f"is empty."
                            ),
                        )
                    )

                    row_has_error = True

                if row_has_error:
                    continue

                # ---------------------------------------------
                # Requirement title is optional
                # ---------------------------------------------

                if not requirement_title:
                    result.warnings.append(
                        ImportFinding(
                            row_number=(
                                row_number
                            ),
                            requirement_id=(
                                requirement_id
                            ),
                            field=(
                                "requirement_title"
                            ),
                            message=(
                                "Requirement title "
                                "is empty."
                            ),
                        )
                    )

                # ---------------------------------------------
                # First row for requirement
                # ---------------------------------------------

                if (
                    requirement_id
                    not in grouped
                ):
                    grouped[
                        requirement_id
                    ] = {
                        "project": project,
                        "title": (
                            requirement_title
                        ),
                        "text": (
                            requirement_text
                        ),
                        "acceptance_criteria": [],
                        "ac_ids": set(),
                    }

                group = grouped[
                    requirement_id
                ]

                # ---------------------------------------------
                # Detect inconsistent repeated requirement data
                # ---------------------------------------------

                if (
                    group["project"]
                    != project
                ):
                    result.errors.append(
                        ImportFinding(
                            row_number=(
                                row_number
                            ),
                            requirement_id=(
                                requirement_id
                            ),
                            field="project",
                            message=(
                                "Requirement is "
                                "associated with "
                                "multiple project "
                                "values."
                            ),
                        )
                    )

                    continue

                if (
                    group["text"]
                    != requirement_text
                ):
                    result.errors.append(
                        ImportFinding(
                            row_number=(
                                row_number
                            ),
                            requirement_id=(
                                requirement_id
                            ),
                            field=(
                                "requirement_text"
                            ),
                            message=(
                                "Repeated requirement "
                                "ID contains different "
                                "requirement text."
                            ),
                        )
                    )

                    continue

                if (
                    group["title"]
                    != requirement_title
                ):
                    result.errors.append(
                        ImportFinding(
                            row_number=(
                                row_number
                            ),
                            requirement_id=(
                                requirement_id
                            ),
                            field=(
                                "requirement_title"
                            ),
                            message=(
                                "Repeated requirement "
                                "ID contains different "
                                "requirement titles."
                            ),
                        )
                    )

                    continue

                # ---------------------------------------------
                # AC IDs must be unique within requirement
                # ---------------------------------------------

                if ac_id in group["ac_ids"]:
                    result.errors.append(
                        ImportFinding(
                            row_number=(
                                row_number
                            ),
                            requirement_id=(
                                requirement_id
                            ),
                            field="ac_id",
                            message=(
                                "Duplicate acceptance "
                                "criterion ID within "
                                "requirement: "
                                f"{ac_id}"
                            ),
                        )
                    )

                    continue

                group["ac_ids"].add(
                    ac_id
                )

                group[
                    "acceptance_criteria"
                ].append(
                    AcceptanceCriterion(
                        id=ac_id,
                        text=ac_text,
                    )
                )

    except UnicodeDecodeError as exc:
        result.errors.append(
            ImportFinding(
                message=(
                    "CSV file could not be decoded "
                    f"as UTF-8: {exc}"
                )
            )
        )

        return result

    except csv.Error as exc:
        result.errors.append(
            ImportFinding(
                message=(
                    "CSV parsing failed: "
                    f"{exc}"
                )
            )
        )

        return result

    # ---------------------------------------------------------
    # Normalize successfully collected requirements
    # ---------------------------------------------------------

    for (
        requirement_id,
        group,
    ) in grouped.items():
        requirement = Requirement(
            requirement_id=(
                requirement_id
            ),
            title=(
                group["title"] or None
            ),
            text=group["text"],
            acceptance_criteria=(
                group[
                    "acceptance_criteria"
                ]
            ),
        )

        result.imported_requirements.append(
            ImportedRequirement(
                project=group["project"],
                requirement=requirement,
            )
        )

    result.requirement_count = len(
        result.imported_requirements
    )

    result.acceptance_criteria_count = sum(
        len(
            item.requirement
            .acceptance_criteria
        )
        for item
        in result.imported_requirements
    )

    return result