from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agent.scenario_orchestrator import (
    run_scenario_pipeline,
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
            "The system shall display a "
            "timeout warning."
        ),
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-01",
                text=(
                    "The timeout warning "
                    "is displayed."
                ),
            )
        ],
    )


def create_supplied_scenarios(
    with_actions=True,
):
    return SuppliedScenarioCollection(
        scenarios=[
            SuppliedTestScenario(
                source_scenario_id="SRC-001",
                title="Timeout warning",
                preconditions=[
                    "User is authenticated."
                ],
                actions=(
                    [
                        "Leave the session inactive."
                    ]
                    if with_actions
                    else []
                ),
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


def create_normalization():
    return ScenarioNormalizationResult(
        normalized_scenarios=[
            ScenarioModel(
                scenario_id="TS-001",
                title="Timeout warning",
                objective=(
                    "Verify the timeout warning."
                ),
                test_type=(
                    ScenarioTestType.HAPPY_PATH
                ),
                preconditions=[
                    "User is authenticated."
                ],
                actions=[
                    "Leave the session inactive."
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
                    "the supplied behavior."
                ),
            )
        ],
    )


def create_passing_coverage():
    return SimpleNamespace(
        uncovered_requirement_ids=[],
        uncovered_acceptance_criteria_ids=[],
        unaccounted_acceptance_criteria_ids=[],
        blocked_acceptance_criteria_ids=[],
        orphan_scenario_ids=[],
        invalid_requirement_references=[],
        invalid_acceptance_criteria_references=[],
        duplicate_scenario_ids=[],
    )


def create_failing_coverage():
    return SimpleNamespace(
        uncovered_requirement_ids=[
            "REQ-001"
        ],
        uncovered_acceptance_criteria_ids=[
            "AC-01"
        ],
        unaccounted_acceptance_criteria_ids=[],
        blocked_acceptance_criteria_ids=[],
        orphan_scenario_ids=[],
        invalid_requirement_references=[],
        invalid_acceptance_criteria_references=[],
        duplicate_scenario_ids=[],
    )


def common_patches():
    """
    Return patchers for dependencies that are not the
    behavior under test.

    VVDesignPackageV1 is patched so these tests verify
    orchestration behavior independently of package
    serialization.
    """

    return [
        patch(
            "agent.scenario_orchestrator."
            "analyze_requirement",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator."
            "analyze_ambiguities",
            return_value=SimpleNamespace(
                findings=[]
            ),
        ),
        patch(
            "agent.scenario_orchestrator."
            "analyze_dispositions",
            return_value=SimpleNamespace(
                dispositions=[]
            ),
        ),
        patch(
            "agent.scenario_orchestrator."
            "validate_dispositions",
            return_value={
                "valid": True
            },
        ),
        patch(
            "agent.scenario_orchestrator."
            "group_scenarios",
            return_value=SimpleNamespace(
                groups=[]
            ),
        ),
        patch(
            "agent.scenario_orchestrator."
            "generate_jama_test_cases",
            return_value=SimpleNamespace(
                test_cases=[]
            ),
        ),
        patch(
            "agent.scenario_orchestrator."
            "generate_bdd_features",
            return_value=SimpleNamespace(
                features=[]
            ),
        ),
        patch(
            "agent.scenario_orchestrator."
            "validate_jama_output",
            return_value={
                "valid": True,
                "errors": [],
            },
        ),
        patch(
            "agent.scenario_orchestrator."
            "validate_bdd_output",
            return_value={
                "valid": True,
                "errors": [],
            },
        ),
        patch(
            "agent.scenario_orchestrator."
            "evaluate_quality_gate",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator."
            "VVScenarioDesignPackageV1",
            return_value=MagicMock(),
        ),
                patch(
            "agent.scenario_orchestrator."
            "evaluate_quality_gate",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator."
            "VVScenarioDesignPackageV1",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator."
            "evaluate_scenario_quality_gate",
            return_value=MagicMock(),
        ),
    ]


def start_patchers(patchers):
    mocks = [
        patcher.start()
        for patcher in patchers
    ]

    return mocks


def stop_patchers(patchers):
    for patcher in reversed(patchers):
        patcher.stop()


def test_valid_source_reaches_normalization():
    patchers = common_patches()

    mocks = start_patchers(
        patchers
    )

    try:
        with (
            patch(
                "agent.scenario_orchestrator."
                "normalize_supplied_scenarios",
                return_value=(
                    create_normalization()
                ),
            ) as mock_normalize,
            patch(
                "agent.scenario_orchestrator."
                "validate_scenario_normalization",
                return_value=(
                    SimpleNamespace(
                        valid=True
                    )
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "calculate_coverage",
                return_value=(
                    create_passing_coverage()
                ),
            ),
        ):
            run_scenario_pipeline(
                project="ActiveConnect",
                requirement=(
                    create_requirement()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios()
                ),
            )

        mock_normalize.assert_called_once()

    finally:
        stop_patchers(
            patchers
        )


def test_invalid_source_never_reaches_cursor():
    patchers = common_patches()

    start_patchers(
        patchers
    )

    try:
        with (
            patch(
                "agent.scenario_orchestrator."
                "normalize_supplied_scenarios"
            ) as mock_normalize,
            patch(
                "agent.scenario_orchestrator."
                "calculate_coverage",
                return_value=(
                    create_failing_coverage()
                ),
            ),
        ):
            run_scenario_pipeline(
                project="ActiveConnect",
                requirement=(
                    create_requirement()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios(
                        with_actions=False
                    )
                ),
            )

        mock_normalize.assert_not_called()

    finally:
        stop_patchers(
            patchers
        )


def test_invalid_normalization_blocks_jama_and_bdd():
    patchers = common_patches()

    mocks = start_patchers(
        patchers
    )

    try:
        jama_mock = mocks[5]
        bdd_mock = mocks[6]

        with (
            patch(
                "agent.scenario_orchestrator."
                "normalize_supplied_scenarios",
                return_value=(
                    create_normalization()
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "validate_scenario_normalization",
                return_value=(
                    SimpleNamespace(
                        valid=False
                    )
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "calculate_coverage",
                return_value=(
                    create_failing_coverage()
                ),
            ),
        ):
            run_scenario_pipeline(
                project="ActiveConnect",
                requirement=(
                    create_requirement()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios()
                ),
            )

        jama_mock.assert_not_called()
        bdd_mock.assert_not_called()

    finally:
        stop_patchers(
            patchers
        )


def test_coverage_failure_blocks_jama_and_bdd():
    patchers = common_patches()

    mocks = start_patchers(
        patchers
    )

    try:
        jama_mock = mocks[5]
        bdd_mock = mocks[6]

        with (
            patch(
                "agent.scenario_orchestrator."
                "normalize_supplied_scenarios",
                return_value=(
                    create_normalization()
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "validate_scenario_normalization",
                return_value=(
                    SimpleNamespace(
                        valid=True
                    )
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "calculate_coverage",
                return_value=(
                    create_failing_coverage()
                ),
            ),
        ):
            run_scenario_pipeline(
                project="ActiveConnect",
                requirement=(
                    create_requirement()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios()
                ),
            )

        jama_mock.assert_not_called()
        bdd_mock.assert_not_called()

    finally:
        stop_patchers(
            patchers
        )


def test_normalized_scenarios_enter_downstream_pipeline():
    patchers = common_patches()

    mocks = start_patchers(
        patchers
    )

    try:
        grouping_mock = mocks[4]
        jama_mock = mocks[5]
        bdd_mock = mocks[6]

        with (
            patch(
                "agent.scenario_orchestrator."
                "normalize_supplied_scenarios",
                return_value=(
                    create_normalization()
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "validate_scenario_normalization",
                return_value=(
                    SimpleNamespace(
                        valid=True
                    )
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "calculate_coverage",
                return_value=(
                    create_passing_coverage()
                ),
            ) as coverage_mock,
        ):
            run_scenario_pipeline(
                project="ActiveConnect",
                requirement=(
                    create_requirement()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios()
                ),
            )

        coverage_call = (
            coverage_mock.call_args.kwargs
        )

        scenarios = (
            coverage_call["scenarios"]
        )

        assert len(scenarios) == 1

        assert (
            scenarios[0].scenario_id
            == "TS-001"
        )

        assert (
            scenarios[0].source
            == "supplied"
        )

        grouping_mock.assert_called_once()
        jama_mock.assert_called_once()
        bdd_mock.assert_called_once()

    finally:
        stop_patchers(
            patchers
        )


def test_requirement_driven_generator_is_not_used():
    """
    Scenario-driven orchestration must obtain master
    scenarios from normalization, not generate_scenarios().
    """

    patchers = common_patches()

    start_patchers(
        patchers
    )

    try:
        with (
            patch(
                "agent.orchestrator."
                "generate_scenarios"
            ) as requirement_generator,
            patch(
                "agent.scenario_orchestrator."
                "normalize_supplied_scenarios",
                return_value=(
                    create_normalization()
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "validate_scenario_normalization",
                return_value=(
                    SimpleNamespace(
                        valid=True
                    )
                ),
            ),
            patch(
                "agent.scenario_orchestrator."
                "calculate_coverage",
                return_value=(
                    create_passing_coverage()
                ),
            ),
        ):
            run_scenario_pipeline(
                project="ActiveConnect",
                requirement=(
                    create_requirement()
                ),
                supplied_scenarios=(
                    create_supplied_scenarios()
                ),
            )

        requirement_generator.assert_not_called()

    finally:
        stop_patchers(
            patchers
        )