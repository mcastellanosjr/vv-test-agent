from models.quality import (
    QualityGateResult,
    QualityGateStatus,
)
from models.scenario_normalization import (
    ScenarioNormalizationResult,
    ScenarioNormalizationStatus,
)
from models.scenario_normalization_validation import (
    ScenarioNormalizationValidationResult,
)
from models.scenario_validation import (
    SuppliedScenarioValidationResult,
)


def evaluate_scenario_quality_gate(
    base_quality_gate: QualityGateResult,
    source_validation: SuppliedScenarioValidationResult,
    normalization: ScenarioNormalizationResult | None,
    normalization_validation: (
        ScenarioNormalizationValidationResult | None
    ),
) -> QualityGateResult:
    """
    Apply scenario-driven validation requirements to the
    existing deterministic V&V quality gate.

    FAIL:
        Invalid supplied scenarios, missing normalization,
        or invalid normalization validation.

    REVIEW:
        At least one supplied scenario was LIMITED or REJECTED.

    PASS:
        No additional scenario-driven issues and the
        base quality gate passes.
    """

    result = base_quality_gate.model_copy(deep=True)

    blocking_reasons = list(result.blocking_reasons)
    review_reasons = list(result.review_reasons)

    # ---------------------------------------------------------
    # Supplied scenario source validation
    # ---------------------------------------------------------

    if not source_validation.valid:
        blocking_reasons.append(
            "Supplied scenario source validation failed."
        )

    # ---------------------------------------------------------
    # Normalization execution
    # ---------------------------------------------------------

    if normalization is None:
        blocking_reasons.append(
            "Scenario normalization was not completed."
        )

    # ---------------------------------------------------------
    # Normalization validation
    # ---------------------------------------------------------

    if normalization_validation is None:
        blocking_reasons.append(
            "Scenario normalization validation was not run."
        )

    elif not normalization_validation.valid:
        blocking_reasons.append(
            "Scenario normalization validation failed."
        )

    # ---------------------------------------------------------
    # Normalization dispositions
    # ---------------------------------------------------------

    if normalization is not None:
        limited_count = sum(
            1
            for record in normalization.records
            if record.status
            == ScenarioNormalizationStatus.LIMITED
        )

        rejected_count = sum(
            1
            for record in normalization.records
            if record.status
            == ScenarioNormalizationStatus.REJECTED
        )

        if limited_count:
            review_reasons.append(
                f"{limited_count} supplied scenario(s) "
                "were normalized with limitations."
            )

        if rejected_count:
            review_reasons.append(
                f"{rejected_count} supplied scenario(s) "
                "were rejected during normalization "
                "and require human review."
            )

    # ---------------------------------------------------------
    # Deterministic final status
    # ---------------------------------------------------------

    result.blocking_reasons = list(
        dict.fromkeys(blocking_reasons)
    )

    result.review_reasons = list(
        dict.fromkeys(review_reasons)
    )

    if result.blocking_reasons:
        result.status = QualityGateStatus.FAIL

    elif result.review_reasons:
        result.status = QualityGateStatus.REVIEW

    else:
        result.status = QualityGateStatus.PASS

    return result