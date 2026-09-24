from agent.supplied_scenario_validator import (
    validate_supplied_scenarios,
)
from models.requirement import (
    AcceptanceCriterion,
    Requirement,
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
                text=(
                    "The warning is displayed."
                ),
            ),
            AcceptanceCriterion(
                id="AC-02",
                text=(
                    "The user is signed out."
                ),
            ),
        ],
    )


def create_valid_scenario(
    scenario_id="SRC-001",
):
    return SuppliedTestScenario(
        source_scenario_id=(
            scenario_id
        ),
        title="Session timeout warning",
        preconditions=[
            "User is authenticated."
        ],
        actions=[
            "Leave the session inactive."
        ],
        expected_results=[
            (
                "The timeout warning "
                "is displayed."
            )
        ],
        requirement_ids=[
            "REQ-001"
        ],
        acceptance_criteria_ids=[
            "AC-01"
        ],
    )


def test_valid_supplied_scenario():
    requirement = (
        create_requirement()
    )

    collection = (
        SuppliedScenarioCollection(
            scenarios=[
                create_valid_scenario()
            ]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is True
    assert result.errors == []

    assert result.scenario_count == 1

    assert (
        result.valid_scenario_count
        == 1
    )

    assert (
        result.invalid_scenario_count
        == 0
    )


def test_duplicate_scenario_id_is_error():
    requirement = (
        create_requirement()
    )

    collection = (
        SuppliedScenarioCollection(
            scenarios=[
                create_valid_scenario(
                    "SRC-001"
                ),
                create_valid_scenario(
                    "SRC-001"
                ),
            ]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is False

    assert any(
        issue.field
        == "source_scenario_id"
        for issue in result.errors
    )

    assert (
        result.invalid_scenario_count
        == 2
    )


def test_missing_actions_is_error():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.actions = []

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is False

    assert any(
        issue.field == "actions"
        for issue in result.errors
    )


def test_missing_expected_results_is_error():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.expected_results = []

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is False

    assert any(
        issue.field
        == "expected_results"
        for issue in result.errors
    )


def test_missing_requirement_traceability_is_error():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.requirement_ids = []

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is False

    assert any(
        issue.field
        == "requirement_ids"
        for issue in result.errors
    )


def test_unknown_requirement_is_error():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.requirement_ids = [
        "REQ-999"
    ]

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is False

    assert any(
        "REQ-999"
        in issue.message
        for issue in result.errors
    )


def test_unknown_ac_is_error():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.acceptance_criteria_ids = [
        "AC-99"
    ]

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is False

    assert any(
        "AC-99"
        in issue.message
        for issue in result.errors
    )


def test_missing_ac_traceability_is_warning():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.acceptance_criteria_ids = []

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is True

    assert any(
        issue.field
        == "acceptance_criteria_ids"
        for issue in result.warnings
    )


def test_missing_preconditions_is_warning():
    requirement = (
        create_requirement()
    )

    scenario = (
        create_valid_scenario()
    )

    scenario.preconditions = []

    collection = (
        SuppliedScenarioCollection(
            scenarios=[scenario]
        )
    )

    result = (
        validate_supplied_scenarios(
            requirement,
            collection,
        )
    )

    assert result.valid is True

    assert any(
        issue.field
        == "preconditions"
        for issue in result.warnings
    )