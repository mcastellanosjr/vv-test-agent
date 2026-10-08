from unittest.mock import MagicMock, patch

from agent.scenario_orchestrator import run_scenario_pipeline
from models.requirement import AcceptanceCriterion, Requirement
from models.supplied_scenario import (
    SuppliedScenarioCollection,
    SuppliedTestScenario,
)
from models.scenario_validation import (
    SuppliedScenarioValidationResult,
)


def create_inputs():
    requirement = Requirement(
        requirement_id="REQ-001",
        title="Session Timeout",
        text="The system shall display a timeout warning.",
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-01",
                text="The timeout warning is displayed.",
            )
        ],
    )

    supplied = SuppliedScenarioCollection(
        scenarios=[
            SuppliedTestScenario(
                source_scenario_id="SRC-001",
                title="Timeout warning",
                actions=["Leave the session inactive."],
                expected_results=["The timeout warning is displayed."],
                requirement_ids=["REQ-001"],
                acceptance_criteria_ids=["AC-01"],
            )
        ]
    )

    return requirement, supplied


def test_source_validation_evidence_is_passed_to_package():
    requirement, supplied = create_inputs()

    source_validation = SuppliedScenarioValidationResult(
        valid=False,
        scenario_count=1,
        valid_scenario_count=0,
        invalid_scenario_count=1,
    )

    with (
        patch(
            "agent.scenario_orchestrator.analyze_requirement",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator.analyze_ambiguities",
            return_value=MagicMock(findings=[]),
        ),
        patch(
            "agent.scenario_orchestrator.analyze_dispositions",
            return_value=MagicMock(dispositions=[]),
        ),
        patch(
            "agent.scenario_orchestrator.validate_dispositions",
            return_value={"valid": True},
        ),
        patch(
            "agent.scenario_orchestrator.validate_supplied_scenarios",
            return_value=source_validation,
        ),
        patch(
            "agent.scenario_orchestrator.calculate_coverage",
            return_value=MagicMock(
                uncovered_requirement_ids=["REQ-001"],
                uncovered_acceptance_criteria_ids=["AC-01"],
                unaccounted_acceptance_criteria_ids=[],
                blocked_acceptance_criteria_ids=[],
                orphan_scenario_ids=[],
                invalid_requirement_references=[],
                invalid_acceptance_criteria_references=[],
                duplicate_scenario_ids=[],
            ),
        ),
        patch(
            "agent.scenario_orchestrator.evaluate_quality_gate",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator."
            "evaluate_scenario_quality_gate",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator.VVScenarioDesignPackageV1",
            return_value=MagicMock(),
        ) as package_mock,
        patch(
            "agent.scenario_orchestrator.normalize_supplied_scenarios",
        ) as normalizer_mock,
    ):
        run_scenario_pipeline(
            project="ActiveConnect",
            requirement=requirement,
            supplied_scenarios=supplied,
        )

    normalizer_mock.assert_not_called()
    package_mock.assert_called_once()

    fields = package_mock.call_args.kwargs

    assert fields["supplied_scenarios"] is supplied
    assert fields["source_validation"] is source_validation
    assert fields["normalization"] is None
    assert fields["normalization_validation"] is None

def test_successful_normalization_evidence_is_preserved():
    from types import SimpleNamespace

    from models.scenario import TestScenario, TestType
    from models.scenario_normalization import (
        ScenarioNormalizationRecord,
        ScenarioNormalizationResult,
        ScenarioNormalizationStatus,
    )
    from models.scenario_normalization_validation import (
        ScenarioNormalizationValidationResult,
    )

    requirement, supplied = create_inputs()

    normalized = TestScenario(
        scenario_id="TS-001",
        title="Timeout warning",
        objective="Verify that the timeout warning is displayed.",
        test_type=TestType.HAPPY_PATH,
        actions=["Leave the session inactive."],
        expected_behavior=["The timeout warning is displayed."],
        requirement_ids=["REQ-001"],
        acceptance_criteria_ids=["AC-01"],
        source="supplied",
    )

    normalization = ScenarioNormalizationResult(
        normalized_scenarios=[normalized],
        records=[
            ScenarioNormalizationRecord(
                source_scenario_id="SRC-001",
                status=ScenarioNormalizationStatus.ACCEPTED,
                normalized_scenario_ids=["TS-001"],
                rationale="The scenario verifies the specified behavior.",
            )
        ],
    )

    normalization_validation = (
        ScenarioNormalizationValidationResult(valid=True)
    )

    coverage = SimpleNamespace(
        uncovered_requirement_ids=[],
        uncovered_acceptance_criteria_ids=[],
        unaccounted_acceptance_criteria_ids=[],
        blocked_acceptance_criteria_ids=[],
        orphan_scenario_ids=[],
        invalid_requirement_references=[],
        invalid_acceptance_criteria_references=[],
        duplicate_scenario_ids=[],
    )

    with (
        patch(
            "agent.scenario_orchestrator.analyze_requirement",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator.analyze_ambiguities",
            return_value=MagicMock(findings=[]),
        ),
        patch(
            "agent.scenario_orchestrator.analyze_dispositions",
            return_value=MagicMock(dispositions=[]),
        ),
        patch(
            "agent.scenario_orchestrator.validate_dispositions",
            return_value={"valid": True},
        ),
        patch(
            "agent.scenario_orchestrator.validate_supplied_scenarios",
            return_value=SuppliedScenarioValidationResult(
                valid=True,
                scenario_count=1,
                valid_scenario_count=1,
                invalid_scenario_count=0,
            ),
        ),
        patch(
            "agent.scenario_orchestrator.normalize_supplied_scenarios",
            return_value=normalization,
        ),
        patch(
            "agent.scenario_orchestrator.validate_scenario_normalization",
            return_value=normalization_validation,
        ),
        patch(
            "agent.scenario_orchestrator.calculate_coverage",
            return_value=coverage,
        ),
        patch(
            "agent.scenario_orchestrator.group_scenarios",
            return_value=SimpleNamespace(groups=[]),
        ),
        patch(
            "agent.scenario_orchestrator.generate_jama_test_cases",
            return_value=SimpleNamespace(test_cases=[]),
        ),
        patch(
            "agent.scenario_orchestrator.generate_bdd_features",
            return_value=SimpleNamespace(features=[]),
        ),
        patch(
            "agent.scenario_orchestrator.validate_jama_output",
            return_value={"valid": True, "errors": []},
        ),
        patch(
            "agent.scenario_orchestrator.validate_bdd_output",
            return_value={"valid": True, "errors": []},
        ),
        patch(
            "agent.scenario_orchestrator.evaluate_quality_gate",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator."
            "evaluate_scenario_quality_gate",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator.VVScenarioDesignPackageV1",
            return_value=MagicMock(),
        ) as package_mock,
    ):
        run_scenario_pipeline(
            project="ActiveConnect",
            requirement=requirement,
            supplied_scenarios=supplied,
        )

    package_mock.assert_called_once()

    fields = package_mock.call_args.kwargs

    assert fields["supplied_scenarios"] is supplied
    assert fields["normalization"] is normalization
    assert fields["normalization_validation"] is normalization_validation

    record = fields["normalization"].records[0]

    assert record.source_scenario_id == "SRC-001"
    assert record.normalized_scenario_ids == ["TS-001"]
    assert fields["test_scenarios"][0].scenario_id == "TS-001"

def test_invalid_source_produces_failed_quality_gate():
    from models.quality import (
        QualityGateResult,
        QualityGateStatus,
    )

    requirement, supplied = create_inputs()

    invalid_source = SuppliedScenarioValidationResult(
        valid=False,
        scenario_count=1,
        valid_scenario_count=0,
        invalid_scenario_count=1,
    )

    with (
        patch(
            "agent.scenario_orchestrator.analyze_requirement",
            return_value=MagicMock(),
        ),
        patch(
            "agent.scenario_orchestrator.analyze_ambiguities",
            return_value=MagicMock(findings=[]),
        ),
        patch(
            "agent.scenario_orchestrator.analyze_dispositions",
            return_value=MagicMock(dispositions=[]),
        ),
        patch(
            "agent.scenario_orchestrator.validate_dispositions",
            return_value={"valid": True},
        ),
        patch(
            "agent.scenario_orchestrator.validate_supplied_scenarios",
            return_value=invalid_source,
        ),
        patch(
            "agent.scenario_orchestrator.calculate_coverage",
            return_value=MagicMock(
                uncovered_requirement_ids=["REQ-001"],
                uncovered_acceptance_criteria_ids=["AC-01"],
                unaccounted_acceptance_criteria_ids=[],
                blocked_acceptance_criteria_ids=[],
                orphan_scenario_ids=[],
                invalid_requirement_references=[],
                invalid_acceptance_criteria_references=[],
                duplicate_scenario_ids=[],
            ),
        ),
        patch(
            "agent.scenario_orchestrator.evaluate_quality_gate",
            return_value=QualityGateResult(
                status=QualityGateStatus.FAIL,
                blocking_reasons=[
                    "JAMA and BDD validation were not run."
                ],
            ),
        ),
        patch(
            "agent.scenario_orchestrator.VVScenarioDesignPackageV1",
            return_value=MagicMock(),
        ) as package_mock,
        patch(
            "agent.scenario_orchestrator.normalize_supplied_scenarios",
        ) as normalizer_mock,
    ):
        run_scenario_pipeline(
            project="ActiveConnect",
            requirement=requirement,
            supplied_scenarios=supplied,
        )

    normalizer_mock.assert_not_called()
    package_mock.assert_called_once()

    quality_gate = (
        package_mock.call_args.kwargs["quality_gate"]
    )

    assert quality_gate.status == QualityGateStatus.FAIL

    assert any(
        "source validation failed" in reason
        for reason in quality_gate.blocking_reasons
    )