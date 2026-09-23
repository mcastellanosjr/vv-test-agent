import pytest

from imported_batch_main import (
    validate_staged_input,
)


def test_validate_staged_input(
    tmp_path,
):
    first = tmp_path / "REQ-002.json"
    second = tmp_path / "REQ-001.json"

    first.write_text(
        "{}",
        encoding="utf-8",
    )

    second.write_text(
        "{}",
        encoding="utf-8",
    )

    files = validate_staged_input(
        tmp_path
    )

    assert len(files) == 2

    assert [
        path.name
        for path in files
    ] == [
        "REQ-001.json",
        "REQ-002.json",
    ]


def test_missing_staging_directory(
    tmp_path,
):
    missing = (
        tmp_path
        / "does-not-exist"
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "does not exist"
        ),
    ):
        validate_staged_input(
            missing
        )


def test_empty_staging_directory(
    tmp_path,
):
    with pytest.raises(
        RuntimeError,
        match=(
            "No staged requirement"
        ),
    ):
        validate_staged_input(
            tmp_path
        )


def test_non_json_files_are_ignored(
    tmp_path,
):
    json_file = (
        tmp_path / "REQ-001.json"
    )

    text_file = (
        tmp_path / "notes.txt"
    )

    json_file.write_text(
        "{}",
        encoding="utf-8",
    )

    text_file.write_text(
        "Not a requirement.",
        encoding="utf-8",
    )

    files = validate_staged_input(
        tmp_path
    )

    assert len(files) == 1

    assert (
        files[0].name
        == "REQ-001.json"
    )