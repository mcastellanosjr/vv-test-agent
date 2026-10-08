from agent.scenario_quality_gate import (
    evaluate_scenario_quality_gate,
)
from models.quality import (
    QualityGateResult,
    QualityGateStatus,
)
from models.scenario_normalization import (
    ScenarioNormalizationRecord,
    ScenarioNormalizationResult,
    ScenarioNormalizationStatus,
)
from models.scenario_normalization_validation import (
    ScenarioNormalizationValidationResult,
)
from models.scenario_validation import (
    SuppliedScenarioValidationResult,
)


def base_gate(
    status=QualityGateStatus.PASS,
):
    return QualityGateResult(
        status=status,
        blocking_reasons=(
            ["Existing blocking reason."]
            if status == QualityGateStatus.FAIL
            else []
        ),
        review_reasons=(
            ["Existing review reason."]
            if status == QualityGateStatus.REVIEW
            else []
        ),
        requirement_coverage_percent=100.0,
        acceptance_criteria_coverage_percent=100.0,
        jama_valid=True,
        bdd_valid=True,
    )


def source_validation(valid=True):
    return SuppliedScenarioValidationResult(
        valid=valid,
        scenario_count=1,
        valid_scenario_count=1 if valid else 0,
        invalid_scenario_count=0 if valid else 1,
    )


def normalization(status=ScenarioNormalizationStatus.ACCEPTED):
    normalized_ids = (
        []
        if status == ScenarioNormalizationStatus.REJECTED
        else ["TS-001"]
    )

    return ScenarioNormalizationResult(
        normalized_scenarios=[],
        records=[
            ScenarioNormalizationRecord(
                source_scenario_id="SRC-001",
                status=status,
                normalized_scenario_ids=normalized_ids,
                rationale="Verification disposition.",
            )
        ],
    )


def normalization_validation(valid=True):
    return ScenarioNormalizationValidationResult(
        valid=valid
    )


def test_all_valid_preserves_pass():
    result = evaluate_scenario_quality_gate(
        base_gate(),
        source_validation(),
        normalization(),
        normalization_validation(),
    )

    assert result.status == QualityGateStatus.PASS


def test_invalid_source_forces_fail():
    result = evaluate_scenario_quality_gate(
        base_gate(),
        source_validation(valid=False),
        None,
        None,
    )

    assert result.status == QualityGateStatus.FAIL
    assert any(
        "source validation failed" in reason
        for reason in result.blocking_reasons
    )


def test_missing_normalization_forces_fail():
    result = evaluate_scenario_quality_gate(
        base_gate(),
        source_validation(),
        None,
        None,
    )

    assert result.status == QualityGateStatus.FAIL


def test_invalid_normalization_forces_fail():
    result = evaluate_scenario_quality_gate(
        base_gate(),
        source_validation(),
        normalization(),
        normalization_validation(valid=False),
    )

    assert result.status == QualityGateStatus.FAIL


def test_limited_scenario_requires_review():
    result = evaluate_scenario_quality_gate(
        base_gate(),
        source_validation(),
        normalization(ScenarioNormalizationStatus.LIMITED),
        normalization_validation(),
    )

    assert result.status == QualityGateStatus.REVIEW


def test_rejected_scenario_requires_review():
    result = evaluate_scenario_quality_gate(
        base_gate(),
        source_validation(),
        normalization(ScenarioNormalizationStatus.REJECTED),
        normalization_validation(),
    )

    assert result.status == QualityGateStatus.REVIEW


def test_existing_fail_cannot_be_downgraded():
    result = evaluate_scenario_quality_gate(
        base_gate(QualityGateStatus.FAIL),
        source_validation(),
        normalization(),
        normalization_validation(),
    )

    assert result.status == QualityGateStatus.FAIL
    assert "Existing blocking reason." in result.blocking_reasons


def test_existing_review_is_preserved():
    result = evaluate_scenario_quality_gate(
        base_gate(QualityGateStatus.REVIEW),
        source_validation(),
        normalization(),
        normalization_validation(),
    )

    assert result.status == QualityGateStatus.REVIEW
    assert "Existing review reason." in result.review_reasons


def test_base_quality_gate_is_not_mutated():
    original = base_gate()

    evaluate_scenario_quality_gate(
        original,
        source_validation(valid=False),
        None,
        None,
    )

    assert original.status == QualityGateStatus.PASS
    assert original.blocking_reasons == []