import json

import pytest

from importers.requirement_stager import (
    safe_filename,
    stage_import_result,
    stage_imported_requirement,
)
from models.import_result import (
    ImportFinding,
    ImportedRequirement,
    RequirementImportResult,
)
from models.requirement import (
    AcceptanceCriterion,
    Requirement,
)


def create_imported_requirement():
    return ImportedRequirement(
        project="ActiveConnect",
        requirement=Requirement(
            requirement_id=(
                "GALAXY1-REQ-001"
            ),
            title="Session Timeout",
            text=(
                "The system shall automatically "
                "sign out an inactive user."
            ),
            acceptance_criteria=[
                AcceptanceCriterion(
                    id="AC-01",
                    text=(
                        "The warning is displayed."
                    ),
                ),
                AcceptanceCriterion(
                    id="AC-02",
                    text=(
                        "The user can continue "
                        "the session."
                    ),
                ),
            ],
        ),
    )


def test_safe_filename():
    assert (
        safe_filename(
            "GALAXY1-REQ-001"
        )
        == "GALAXY1-REQ-001"
    )

    assert (
        safe_filename(
            "REQ:001/TEST"
        )
        == "REQ_001_TEST"
    )


def test_stage_imported_requirement(
    tmp_path,
):
    imported = (
        create_imported_requirement()
    )

    output_path = (
        stage_imported_requirement(
            imported_requirement=imported,
            output_directory=tmp_path,
        )
    )

    assert output_path.exists()

    assert (
        output_path.name
        == "GALAXY1-REQ-001.json"
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["project"]
        == "ActiveConnect"
    )

    assert (
        payload["requirement"]
        ["requirement_id"]
        == "GALAXY1-REQ-001"
    )

    assert (
        len(
            payload["requirement"]
            ["acceptance_criteria"]
        )
        == 2
    )


def test_stage_valid_import_result(
    tmp_path,
):
    imported = (
        create_imported_requirement()
    )

    import_result = (
        RequirementImportResult(
            source_file=(
                "requirements.csv"
            ),
            imported_requirements=[
                imported
            ],
            total_rows=2,
            requirement_count=1,
            acceptance_criteria_count=2,
        )
    )

    staged_files = (
        stage_import_result(
            import_result=import_result,
            output_directory=tmp_path,
        )
    )

    assert len(staged_files) == 1

    assert (
        staged_files[0].name
        == "GALAXY1-REQ-001.json"
    )


def test_invalid_import_cannot_be_staged(
    tmp_path,
):
    import_result = (
        RequirementImportResult(
            source_file=(
                "requirements.csv"
            ),
            errors=[
                ImportFinding(
                    row_number=2,
                    field="requirement_text",
                    message=(
                        "Required field is empty."
                    ),
                )
            ],
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "validation errors"
        ),
    ):
        stage_import_result(
            import_result=import_result,
            output_directory=tmp_path,
        )


def test_staged_file_matches_batch_input_format(
    tmp_path,
):
    imported = (
        create_imported_requirement()
    )

    output_path = (
        stage_imported_requirement(
            imported_requirement=imported,
            output_directory=tmp_path,
        )
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert "project" in payload
    assert "requirement" in payload

    requirement = payload[
        "requirement"
    ]

    assert "requirement_id" in requirement
    assert "title" in requirement
    assert "text" in requirement

    assert (
        "acceptance_criteria"
        in requirement
    )

    assert (
        requirement[
            "acceptance_criteria"
        ][0]["id"]
        == "AC-01"
    )

    assert (
        "text"
        in requirement[
            "acceptance_criteria"
        ][0]
    )