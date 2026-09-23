from importers.csv_requirement_importer import (
    import_requirements_csv,
)


def test_import_multiple_requirements(
    tmp_path,
):
    source = tmp_path / "requirements.csv"

    source.write_text(
        "project,requirement_id,"
        "requirement_title,"
        "requirement_text,"
        "ac_id,ac_text\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,"
        "The system shall sign out.,"
        "AC-01,Warning displayed.\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,"
        "The system shall sign out.,"
        "AC-02,User can continue.\n"
        "ActiveConnect,REQ-002,"
        "Name Length,"
        "The system shall limit names.,"
        "AC-01,Maximum is 40 characters.\n",
        encoding="utf-8",
    )

    result = import_requirements_csv(
        source
    )

    assert result.valid is True
    assert result.errors == []

    assert result.total_rows == 3
    assert result.requirement_count == 2

    assert (
        result.acceptance_criteria_count
        == 3
    )

    first = (
        result.imported_requirements[0]
    )

    assert (
        first.requirement.requirement_id
        == "REQ-001"
    )

    assert (
        len(
            first.requirement
            .acceptance_criteria
        )
        == 2
    )


def test_duplicate_ac_id_is_error(
    tmp_path,
):
    source = tmp_path / "requirements.csv"

    source.write_text(
        "project,requirement_id,"
        "requirement_title,"
        "requirement_text,"
        "ac_id,ac_text\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,"
        "Requirement text,"
        "AC-01,First AC.\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,"
        "Requirement text,"
        "AC-01,Duplicate AC.\n",
        encoding="utf-8",
    )

    result = import_requirements_csv(
        source
    )

    assert result.valid is False

    assert any(
        "Duplicate acceptance"
        in error.message
        for error in result.errors
    )


def test_inconsistent_requirement_text_is_error(
    tmp_path,
):
    source = tmp_path / "requirements.csv"

    source.write_text(
        "project,requirement_id,"
        "requirement_title,"
        "requirement_text,"
        "ac_id,ac_text\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,"
        "Requirement version one,"
        "AC-01,First AC.\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,"
        "Requirement version two,"
        "AC-02,Second AC.\n",
        encoding="utf-8",
    )

    result = import_requirements_csv(
        source
    )

    assert result.valid is False

    assert any(
        "different requirement text"
        in error.message
        for error in result.errors
    )


def test_missing_required_column_is_error(
    tmp_path,
):
    source = tmp_path / "requirements.csv"

    source.write_text(
        "project,requirement_id,"
        "requirement_text,"
        "ac_id\n"
        "ActiveConnect,REQ-001,"
        "Requirement text,"
        "AC-01\n",
        encoding="utf-8",
    )

    result = import_requirements_csv(
        source
    )

    assert result.valid is False

    assert any(
        "missing required columns"
        in error.message
        for error in result.errors
    )


def test_empty_required_value_is_error(
    tmp_path,
):
    source = tmp_path / "requirements.csv"

    source.write_text(
        "project,requirement_id,"
        "requirement_title,"
        "requirement_text,"
        "ac_id,ac_text\n"
        "ActiveConnect,REQ-001,"
        "Session Timeout,,"
        "AC-01,Warning displayed.\n",
        encoding="utf-8",
    )

    result = import_requirements_csv(
        source
    )

    assert result.valid is False

    assert any(
        error.field
        == "requirement_text"
        for error in result.errors
    )


def test_empty_title_is_warning(
    tmp_path,
):
    source = tmp_path / "requirements.csv"

    source.write_text(
        "project,requirement_id,"
        "requirement_title,"
        "requirement_text,"
        "ac_id,ac_text\n"
        "ActiveConnect,REQ-001,,"
        "Requirement text,"
        "AC-01,Warning displayed.\n",
        encoding="utf-8",
    )

    result = import_requirements_csv(
        source
    )

    assert result.valid is True
    assert result.requirement_count == 1

    assert len(result.warnings) == 1

    assert (
        result.warnings[0].field
        == "requirement_title"
    )