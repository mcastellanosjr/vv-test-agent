from unittest.mock import patch

from agent.scenario_normalizer import (
    normalize_supplied_scenarios,
)
from models.analysis import (
    RequirementAnalysis,
)
from models.finding import (
    FindingCollection,
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
                text=(
                    "The warning is displayed."
                ),
            )
        ],
    )


def create_supplied_scenarios():
    return SuppliedScenarioCollection(
        scenarios=[
            SuppliedTestScenario(
                source_scenario_id=(
                    "SRC-001"
                ),
                title=(
                    "Session timeout warning"
                ),
                actions=[
                    (
                        "Leave the session "
                        "inactive."
                    )
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
        ]
    )


def create_normalization_result():
    return ScenarioNormalizationResult(
        normalized_scenarios=[
            ScenarioModel(
                scenario_id="TS-001",
                title=(
                    "Session timeout warning"
                ),
                objective=(
                    "Verify the session "
                    "timeout warning."
                ),
                test_type=(
                    ScenarioTestType
                    .STATE_TRANSITION
                ),
                actions=[
                    (
                        "Leave the session "
                        "inactive."
                    )
                ],
                expected_behavior=[
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
                source="supplied",
            )
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
                    "The supplied scenario "
                    "directly verifies AC-01."
                ),
            )
        ],
    )


def test_normalizer_returns_structured_result():
    expected = (
        create_normalization_result()
    )

    with patch(
        "agent.scenario_normalizer."
        "run_cursor_structured",
        return_value=expected,
    ) as mock_cursor:
        result = (
            normalize_supplied_scenarios(
                requirement=(
                    create_requirement()
                ),
                analysis=(
                    RequirementAnalysis()
                ),
                findings=(
                    FindingCollection()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios()
                ),
            )
        )

    assert result == expected

    mock_cursor.assert_called_once()


def test_normalizer_requests_correct_model():
    expected = (
        create_normalization_result()
    )

    with patch(
        "agent.scenario_normalizer."
        "run_cursor_structured",
        return_value=expected,
    ) as mock_cursor:
        normalize_supplied_scenarios(
            requirement=(
                create_requirement()
            ),
            analysis=(
                RequirementAnalysis()
            ),
            findings=(
                FindingCollection()
            ),
            supplied_scenarios=(
                create_supplied_scenarios()
            ),
        )

    call = mock_cursor.call_args

    assert (
        call.kwargs["response_model"]
        is ScenarioNormalizationResult
    )


def test_prompt_contains_source_scenario():
    expected = (
        create_normalization_result()
    )

    with patch(
        "agent.scenario_normalizer."
        "run_cursor_structured",
        return_value=expected,
    ) as mock_cursor:
        normalize_supplied_scenarios(
            requirement=(
                create_requirement()
            ),
            analysis=(
                RequirementAnalysis()
            ),
            findings=(
                FindingCollection()
            ),
            supplied_scenarios=(
                create_supplied_scenarios()
            ),
        )

    prompt = (
        mock_cursor.call_args
        .kwargs["prompt"]
    )

    assert "SRC-001" in prompt

    assert (
        "Session timeout warning"
        in prompt
    )

    assert (
        "The timeout warning "
        "is displayed."
        in prompt
    )


def test_prompt_contains_source_preservation_rules():
    expected = (
        create_normalization_result()
    )

    with patch(
        "agent.scenario_normalizer."
        "run_cursor_structured",
        return_value=expected,
    ) as mock_cursor:
        normalize_supplied_scenarios(
            requirement=(
                create_requirement()
            ),
            analysis=(
                RequirementAnalysis()
            ),
            findings=(
                FindingCollection()
            ),
            supplied_scenarios=(
                create_supplied_scenarios()
            ),
        )

    prompt = (
        mock_cursor.call_args
        .kwargs["prompt"]
    )

    assert (
        "Do NOT silently replace"
        in prompt
    )

    assert (
        "Do NOT invent"
        in prompt
    )

    assert (
        "Do not create additional scenarios merely to improve"
        in prompt
    )

    assert (
        "requirement coverage."
        in prompt
    )

    assert (
        'source fields equal "supplied"'
        in prompt
    )