from collections import Counter

from models.requirement import Requirement
from models.scenario_validation import (
    ScenarioValidationIssue,
    ScenarioValidationSeverity,
    SuppliedScenarioValidationResult,
)
from models.supplied_scenario import (
    SuppliedScenarioCollection,
)


def validate_supplied_scenarios(
    requirement: Requirement,
    supplied_scenarios: (
        SuppliedScenarioCollection
    ),
) -> SuppliedScenarioValidationResult:
    """
    Deterministically validate supplied test scenarios
    before AI normalization.

    This validator checks structural integrity and
    traceability only. It does not interpret whether
    scenario behavior is semantically correct.
    """

    errors: list[
        ScenarioValidationIssue
    ] = []

    warnings: list[
        ScenarioValidationIssue
    ] = []

    scenarios = (
        supplied_scenarios.scenarios
    )

    valid_requirement_id = (
        requirement.requirement_id
    )

    valid_ac_ids = {
        ac.id
        for ac
        in requirement.acceptance_criteria
    }

    # ---------------------------------------------------------
    # Duplicate source scenario IDs
    # ---------------------------------------------------------

    source_ids = [
        scenario.source_scenario_id
        for scenario
        in scenarios
    ]

    id_counts = Counter(
        source_ids
    )

    duplicate_ids = {
        scenario_id
        for (
            scenario_id,
            count,
        ) in id_counts.items()
        if count > 1
    }

    invalid_scenario_ids: set[
        str
    ] = set()

    for duplicate_id in sorted(
        duplicate_ids
    ):
        errors.append(
            ScenarioValidationIssue(
                source_scenario_id=(
                    duplicate_id
                ),
                severity=(
                    ScenarioValidationSeverity
                    .ERROR
                ),
                field=(
                    "source_scenario_id"
                ),
                message=(
                    "Duplicate supplied scenario "
                    "ID."
                ),
            )
        )

        invalid_scenario_ids.add(
            duplicate_id
        )

    # ---------------------------------------------------------
    # Scenario-level validation
    # ---------------------------------------------------------

    for scenario in scenarios:
        scenario_id = (
            scenario.source_scenario_id
        )

        scenario_has_error = (
            scenario_id
            in duplicate_ids
        )

        # -----------------------------------------------------
        # Actions
        # -----------------------------------------------------

        if not scenario.actions:
            errors.append(
                ScenarioValidationIssue(
                    source_scenario_id=(
                        scenario_id
                    ),
                    severity=(
                        ScenarioValidationSeverity
                        .ERROR
                    ),
                    field="actions",
                    message=(
                        "Supplied scenario does "
                        "not contain any actions."
                    ),
                )
            )

            scenario_has_error = True

        # -----------------------------------------------------
        # Expected results
        # -----------------------------------------------------

        if not scenario.expected_results:
            errors.append(
                ScenarioValidationIssue(
                    source_scenario_id=(
                        scenario_id
                    ),
                    severity=(
                        ScenarioValidationSeverity
                        .ERROR
                    ),
                    field=(
                        "expected_results"
                    ),
                    message=(
                        "Supplied scenario does "
                        "not contain any expected "
                        "results."
                    ),
                )
            )

            scenario_has_error = True

        # -----------------------------------------------------
        # Requirement traceability
        # -----------------------------------------------------

        if not scenario.requirement_ids:
            errors.append(
                ScenarioValidationIssue(
                    source_scenario_id=(
                        scenario_id
                    ),
                    severity=(
                        ScenarioValidationSeverity
                        .ERROR
                    ),
                    field=(
                        "requirement_ids"
                    ),
                    message=(
                        "Supplied scenario does "
                        "not contain requirement "
                        "traceability."
                    ),
                )
            )

            scenario_has_error = True

        else:
            unknown_requirement_ids = [
                requirement_id
                for requirement_id
                in scenario.requirement_ids
                if requirement_id
                != valid_requirement_id
            ]

            for requirement_id in (
                unknown_requirement_ids
            ):
                errors.append(
                    ScenarioValidationIssue(
                        source_scenario_id=(
                            scenario_id
                        ),
                        severity=(
                            ScenarioValidationSeverity
                            .ERROR
                        ),
                        field=(
                            "requirement_ids"
                        ),
                        message=(
                            "Unknown requirement "
                            "reference: "
                            f"{requirement_id}"
                        ),
                    )
                )

                scenario_has_error = True

        # -----------------------------------------------------
        # AC traceability
        # -----------------------------------------------------

        if not (
            scenario
            .acceptance_criteria_ids
        ):
            warnings.append(
                ScenarioValidationIssue(
                    source_scenario_id=(
                        scenario_id
                    ),
                    severity=(
                        ScenarioValidationSeverity
                        .WARNING
                    ),
                    field=(
                        "acceptance_criteria_ids"
                    ),
                    message=(
                        "Supplied scenario does "
                        "not contain acceptance "
                        "criterion traceability."
                    ),
                )
            )

        else:
            for ac_id in (
                scenario
                .acceptance_criteria_ids
            ):
                if ac_id in valid_ac_ids:
                    continue

                errors.append(
                    ScenarioValidationIssue(
                        source_scenario_id=(
                            scenario_id
                        ),
                        severity=(
                            ScenarioValidationSeverity
                            .ERROR
                        ),
                        field=(
                            "acceptance_criteria_ids"
                        ),
                        message=(
                            "Unknown acceptance "
                            "criterion reference: "
                            f"{ac_id}"
                        ),
                    )
                )

                scenario_has_error = True

        # -----------------------------------------------------
        # Preconditions
        #
        # Missing preconditions are not an error because
        # some scenarios legitimately require none.
        # -----------------------------------------------------

        if not scenario.preconditions:
            warnings.append(
                ScenarioValidationIssue(
                    source_scenario_id=(
                        scenario_id
                    ),
                    severity=(
                        ScenarioValidationSeverity
                        .WARNING
                    ),
                    field="preconditions",
                    message=(
                        "Supplied scenario does "
                        "not define preconditions. "
                        "Verify that none are "
                        "required."
                    ),
                )
            )

        if scenario_has_error:
            invalid_scenario_ids.add(
                scenario_id
            )

    scenario_count = len(
        scenarios
    )

    invalid_scenario_count = sum(
        1
        for scenario
        in scenarios
        if (
            scenario.source_scenario_id
            in invalid_scenario_ids
        )
    )

    valid_scenario_count = (
        scenario_count
        - invalid_scenario_count
    )

    return (
        SuppliedScenarioValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            scenario_count=(
                scenario_count
            ),
            valid_scenario_count=(
                valid_scenario_count
            ),
            invalid_scenario_count=(
                invalid_scenario_count
            ),
        )
    )