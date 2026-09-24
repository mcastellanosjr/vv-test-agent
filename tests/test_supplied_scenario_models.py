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
    SuppliedScenarioSource,
    SuppliedTestScenario,
)


def test_supplied_scenario():
    scenario = SuppliedTestScenario(
        source_scenario_id="SRC-001",
        title="Session timeout warning",
        preconditions=[
            "User is authenticated.",
        ],
        actions=[
            (
                "Leave the session inactive "
                "for 4 minutes."
            ),
        ],
        expected_results=[
            (
                "The session timeout warning "
                "is displayed."
            ),
        ],
        requirement_ids=[
            "GALAXY1-REQ-101"
        ],
        acceptance_criteria_ids=[
            "AC-01"
        ],
        source=(
            SuppliedScenarioSource.CSV
        ),
        source_reference=(
            "scenarios.csv row 2"
        ),
    )

    assert (
        scenario.source_scenario_id
        == "SRC-001"
    )

    assert (
        scenario.source
        == SuppliedScenarioSource.CSV
    )

    assert (
        scenario.acceptance_criteria_ids
        == ["AC-01"]
    )


def test_supplied_scenario_collection():
    scenario = SuppliedTestScenario(
        source_scenario_id="SRC-001",
        title="Test scenario",
    )

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    assert len(
        collection.scenarios
    ) == 1


def test_normalization_record():
    record = (
        ScenarioNormalizationRecord(
            source_scenario_id="SRC-001",
            status=(
                ScenarioNormalizationStatus
                .ACCEPTED
            ),
            normalized_scenario_ids=[
                "TS-001"
            ],
            rationale=(
                "Scenario directly verifies "
                "the acceptance criterion."
            ),
        )
    )

    assert (
        record.status
        == ScenarioNormalizationStatus
        .ACCEPTED
    )

    assert (
        record.normalized_scenario_ids
        == ["TS-001"]
    )


def test_limited_normalization_record():
    record = (
        ScenarioNormalizationRecord(
            source_scenario_id="SRC-002",
            status=(
                ScenarioNormalizationStatus
                .LIMITED
            ),
            normalized_scenario_ids=[
                "TS-002"
            ],
            rationale=(
                "Scenario contains usable "
                "verification behavior."
            ),
            limitations=[
                (
                    "Expected result is not "
                    "fully observable."
                )
            ],
        )
    )

    assert (
        record.status
        == ScenarioNormalizationStatus
        .LIMITED
    )

    assert len(
        record.limitations
    ) == 1


def test_normalization_result():
    normalized = ScenarioModel(
        scenario_id="TS-001",
        title="Session timeout warning",
        objective=(
            "Verify the timeout warning."
        ),
        test_type=(
            ScenarioTestType.STATE_TRANSITION
        ),
        preconditions=[
            "User is authenticated."
        ],
        actions=[
            (
                "Leave the session inactive "
                "for 4 minutes."
            )
        ],
        expected_behavior=[
            (
                "The session timeout warning "
                "is displayed."
            )
        ],
        requirement_ids=[
            "GALAXY1-REQ-101"
        ],
        acceptance_criteria_ids=[
            "AC-01"
        ],
        source="supplied",
    )

    record = (
        ScenarioNormalizationRecord(
            source_scenario_id="SRC-001",
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
    )

    result = (
        ScenarioNormalizationResult(
            normalized_scenarios=[
                normalized
            ],
            records=[record],
        )
    )

    assert len(
        result.normalized_scenarios
    ) == 1

    assert len(
        result.records
    ) == 1


def test_rejected_scenario_has_no_normalized_mapping():
    record = (
        ScenarioNormalizationRecord(
            source_scenario_id="SRC-003",
            status=(
                ScenarioNormalizationStatus
                .REJECTED
            ),
            normalized_scenario_ids=[],
            rationale=(
                "Scenario is outside the "
                "requirement scope."
            ),
        )
    )

    assert (
        record.normalized_scenario_ids
        == []
    )