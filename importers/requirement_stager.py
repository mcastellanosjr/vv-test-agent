import json
from pathlib import Path

from models.import_result import (
    ImportedRequirement,
    RequirementImportResult,
)


def safe_filename(
    requirement_id: str,
) -> str:
    """
    Convert a requirement ID into a safe filename.

    Normal requirement IDs such as GALAXY1-REQ-001
    remain unchanged.
    """

    invalid_characters = (
        '<>:"/\\|?*'
    )

    filename = requirement_id.strip()

    for character in invalid_characters:
        filename = filename.replace(
            character,
            "_",
        )

    return filename


def stage_imported_requirement(
    imported_requirement: ImportedRequirement,
    output_directory: Path,
) -> Path:
    """
    Write one normalized requirement JSON file in the
    format already supported by the batch processor.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    requirement = (
        imported_requirement.requirement
    )

    filename = (
        safe_filename(
            requirement.requirement_id
        )
        + ".json"
    )

    output_path = (
        output_directory
        / filename
    )

    payload = {
        "project": (
            imported_requirement.project
        ),
        "requirement": (
            requirement.model_dump(
                mode="json"
            )
        ),
    }

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def stage_import_result(
    import_result: RequirementImportResult,
    output_directory: Path,
) -> list[Path]:
    """
    Stage all successfully normalized requirements.

    Staging is intentionally blocked if the CSV import
    contains any validation errors.
    """

    if not import_result.valid:
        raise ValueError(
            "Requirement import contains validation "
            "errors. Staging is not permitted."
        )

    staged_files: list[Path] = []

    for imported_requirement in (
        import_result.imported_requirements
    ):
        staged_files.append(
            stage_imported_requirement(
                imported_requirement=(
                    imported_requirement
                ),
                output_directory=(
                    output_directory
                ),
            )
        )

    return staged_files