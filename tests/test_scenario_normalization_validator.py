from agent.scenario_normalization_validator import (
    validate_scenario_normalization,
)
from models.requirement import (
    AcceptanceCriterion,
    Requirement,
)
from models.scenario import (
    TestScenario as ScenarioModel,
    TestType as ScenarioTestType,
)
from models.scenario_normalization import (
    ScenarioNormalizationRecord,
    ScenarioNormalizationResult,
    ScenarioNormalizationStatus,
)
from models.supplied_scenario import (
    SuppliedScenarioCollection,
    SuppliedTestScenario,
)


def create_requirement():
    return Requirement(
        requirement_id="REQ-001",
        title="Session Timeout",
        text=(
            "The system shall sign out "
            "inactive users."
        ),
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-01",
                text="Warning displayed.",
            ),
            AcceptanceCriterion(
                id="AC-02",
                text="User signed out.",
            ),
        ],
    )


def create_supplied_collection():
    return SuppliedScenarioCollection(
        scenarios=[
            SuppliedTestScenario(
                source_scenario_id="SRC-001",
                title="Warning",
                actions=[
                    "Leave session inactive."
                ],
                expected_results=[
                    "Warning is displayed."
                ],
                requirement_ids=[
                    "REQ-001"
                ],
                acceptance_criteria_ids=[
                    "AC-01"
                ],
            )
        ]
    )


def create_normalized_scenario(
    scenario_id="TS-001",
    requirement_ids=None,
    acceptance_criteria_ids=None,
):
    return ScenarioModel(
        scenario_id=scenario_id,
        title="Session timeout warning",
        objective=(
            "Verify timeout warning."
        ),
        test_type=(
            ScenarioTestType
            .STATE_TRANSITION
        ),
        actions=[
            "Leave session inactive."
        ],
        expected_behavior=[
            "Warning is displayed."
        ],
        requirement_ids=(
            requirement_ids
            if requirement_ids is not None
            else ["REQ-001"]
        ),
        acceptance_criteria_ids=(
            acceptance_criteria_ids
            if acceptance_criteria_ids
            is not None
            else ["AC-01"]
        ),
        source="supplied",
    )


def create_valid_normalization():
    return ScenarioNormalizationResult(
        normalized_scenarios=[
            create_normalized_scenario()
        ],
        records=[
            ScenarioNormalizationRecord(
                source_scenario_id=(
                    "SRC-001"
                ),
                status=(
                    ScenarioNormalizationStatus
                    .ACCEPTED
                ),
                normalized_scenario_ids=[
                    "TS-001"
                ],
                rationale=(
                    "Scenario is supported."
                ),
            )
        ],
    )


def test_valid_normalization():
    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            create_valid_normalization(),
        )
    )

    assert result.valid is True
    assert result.errors == []


def test_missing_source_record_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.records = []

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        result.missing_source_scenario_ids
        == ["SRC-001"]
    )


def test_unknown_source_record_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.records[0].source_scenario_id = (
        "SRC-999"
    )

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "SRC-999"
        in result.unknown_source_scenario_ids
    )


def test_duplicate_source_record_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.records.append(
        ScenarioNormalizationRecord(
            source_scenario_id=(
                "SRC-001"
            ),
            status=(
                ScenarioNormalizationStatus
                .ACCEPTED
            ),
            normalized_scenario_ids=[
                "TS-001"
            ],
            rationale="Duplicate record.",
        )
    )

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        result.duplicate_source_scenario_ids
        == ["SRC-001"]
    )


def test_accepted_without_mapping_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.records[
        0
    ].normalized_scenario_ids = []

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "SRC-001"
        in result
        .unmapped_accepted_or_limited_ids
    )


def test_rejected_with_mapping_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.records[0].status = (
        ScenarioNormalizationStatus
        .REJECTED
    )

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "SRC-001"
        in result
        .mapped_rejected_scenario_ids
    )


def test_unknown_normalized_mapping_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.records[
        0
    ].normalized_scenario_ids = [
        "TS-999"
    ]

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "TS-999"
        in result
        .unknown_normalized_scenario_ids
    )


def test_orphan_normalized_scenario_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.normalized_scenarios.append(
        create_normalized_scenario(
            scenario_id="TS-002"
        )
    )

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "TS-002"
        in result
        .orphan_normalized_scenario_ids
    )


def test_duplicate_normalized_id_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.normalized_scenarios.append(
        create_normalized_scenario(
            scenario_id="TS-001"
        )
    )

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        result
        .duplicate_normalized_scenario_ids
        == ["TS-001"]
    )


def test_invalid_requirement_reference_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.normalized_scenarios[
        0
    ].requirement_ids = [
        "REQ-999"
    ]

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "REQ-999"
        in result
        .invalid_requirement_references
    )


def test_invalid_ac_reference_is_error():
    normalization = (
        create_valid_normalization()
    )

    normalization.normalized_scenarios[
        0
    ].acceptance_criteria_ids = [
        "AC-99"
    ]

    result = (
        validate_scenario_normalization(
            create_requirement(),
            create_supplied_collection(),
            normalization,
        )
    )

    assert result.valid is False

    assert (
        "AC-99"
        in result
        .invalid_acceptance_criteria_references
    )