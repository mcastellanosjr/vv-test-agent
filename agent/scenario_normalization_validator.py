from collections import Counter

from models.requirement import Requirement
from models.scenario_normalization import (
    ScenarioNormalizationResult,
    ScenarioNormalizationStatus,
)
from models.scenario_normalization_validation import (
    ScenarioNormalizationValidationResult,
)
from models.supplied_scenario import (
    SuppliedScenarioCollection,
)


def find_duplicates(
    values: list[str],
) -> list[str]:
    counts = Counter(values)

    return sorted(
        value
        for value, count
        in counts.items()
        if count > 1
    )


def validate_scenario_normalization(
    requirement: Requirement,
    supplied_scenarios: (
        SuppliedScenarioCollection
    ),
    normalization: (
        ScenarioNormalizationResult
    ),
) -> ScenarioNormalizationValidationResult:
    """
    Deterministically validate AI-produced scenario
    normalization output.

    This function validates identity, mapping and
    traceability integrity. It does not judge semantic
    quality of the normalized scenario text.
    """

    errors: list[str] = []

    source_ids = [
        scenario.source_scenario_id
        for scenario
        in supplied_scenarios.scenarios
    ]

    source_id_set = set(
        source_ids
    )

    record_source_ids = [
        record.source_scenario_id
        for record
        in normalization.records
    ]

    record_source_id_set = set(
        record_source_ids
    )

    normalized_ids = [
        scenario.scenario_id
        for scenario
        in normalization.normalized_scenarios
    ]

    normalized_id_set = set(
        normalized_ids
    )

    # ---------------------------------------------------------
    # Every supplied scenario must receive exactly one record.
    # ---------------------------------------------------------

    missing_source_ids = sorted(
        source_id_set
        - record_source_id_set
    )

    unknown_source_ids = sorted(
        record_source_id_set
        - source_id_set
    )

    duplicate_source_ids = (
        find_duplicates(
            record_source_ids
        )
    )

    if missing_source_ids:
        errors.append(
            "One or more supplied scenarios "
            "do not have a normalization record."
        )

    if unknown_source_ids:
        errors.append(
            "Normalization contains unknown "
            "supplied scenario IDs."
        )

    if duplicate_source_ids:
        errors.append(
            "A supplied scenario has more than "
            "one normalization record."
        )

    # ---------------------------------------------------------
    # Normalized master IDs must be unique.
    # ---------------------------------------------------------

    duplicate_normalized_ids = (
        find_duplicates(
            normalized_ids
        )
    )

    if duplicate_normalized_ids:
        errors.append(
            "Duplicate normalized master "
            "scenario IDs were found."
        )

    # ---------------------------------------------------------
    # Validate record-to-normalized-scenario mappings.
    # ---------------------------------------------------------

    unknown_normalized_ids: set[
        str
    ] = set()

    unmapped_accepted_or_limited: set[
        str
    ] = set()

    mapped_rejected: set[
        str
    ] = set()

    mapped_normalized_ids: list[
        str
    ] = []

    for record in normalization.records:
        if record.status in {
            ScenarioNormalizationStatus.ACCEPTED,
            ScenarioNormalizationStatus.LIMITED,
        }:
            if not record.normalized_scenario_ids:
                unmapped_accepted_or_limited.add(
                    record.source_scenario_id
                )

        if (
            record.status
            == ScenarioNormalizationStatus.REJECTED
            and record.normalized_scenario_ids
        ):
            mapped_rejected.add(
                record.source_scenario_id
            )

        for normalized_id in (
            record.normalized_scenario_ids
        ):
            mapped_normalized_ids.append(
                normalized_id
            )

            if (
                normalized_id
                not in normalized_id_set
            ):
                unknown_normalized_ids.add(
                    normalized_id
                )

    if unknown_normalized_ids:
        errors.append(
            "Normalization records reference "
            "unknown normalized scenario IDs."
        )

    if unmapped_accepted_or_limited:
        errors.append(
            "Accepted or limited supplied "
            "scenarios are missing normalized "
            "scenario mappings."
        )

    if mapped_rejected:
        errors.append(
            "Rejected supplied scenarios must "
            "not map to executable normalized "
            "scenarios."
        )

    # ---------------------------------------------------------
    # A normalized scenario must be mapped from at least
    # one supplied scenario.
    # ---------------------------------------------------------

    mapped_normalized_id_set = set(
        mapped_normalized_ids
    )

    orphan_normalized_ids = sorted(
        normalized_id_set
        - mapped_normalized_id_set
    )

    if orphan_normalized_ids:
        errors.append(
            "One or more normalized scenarios "
            "are not mapped from any supplied "
            "scenario."
        )

    # ---------------------------------------------------------
    # Requirement / AC traceability must remain in scope.
    # ---------------------------------------------------------

    valid_requirement_id = (
        requirement.requirement_id
    )

    valid_ac_ids = {
        ac.id
        for ac
        in requirement.acceptance_criteria
    }

    invalid_requirement_refs: set[
        str
    ] = set()

    invalid_ac_refs: set[
        str
    ] = set()

    for scenario in (
        normalization.normalized_scenarios
    ):
        for requirement_id in (
            scenario.requirement_ids
        ):
            if (
                requirement_id
                != valid_requirement_id
            ):
                invalid_requirement_refs.add(
                    requirement_id
                )

        for ac_id in (
            scenario.acceptance_criteria_ids
        ):
            if ac_id not in valid_ac_ids:
                invalid_ac_refs.add(
                    ac_id
                )

    if invalid_requirement_refs:
        errors.append(
            "Normalized scenarios contain "
            "invalid requirement references."
        )

    if invalid_ac_refs:
        errors.append(
            "Normalized scenarios contain "
            "invalid acceptance criterion "
            "references."
        )

    return (
        ScenarioNormalizationValidationResult(
            valid=not errors,
            errors=errors,
            missing_source_scenario_ids=(
                missing_source_ids
            ),
            unknown_source_scenario_ids=(
                unknown_source_ids
            ),
            duplicate_source_scenario_ids=(
                duplicate_source_ids
            ),
            duplicate_normalized_scenario_ids=(
                duplicate_normalized_ids
            ),
            unknown_normalized_scenario_ids=sorted(
                unknown_normalized_ids
            ),
            unmapped_accepted_or_limited_ids=sorted(
                unmapped_accepted_or_limited
            ),
            mapped_rejected_scenario_ids=sorted(
                mapped_rejected
            ),
            invalid_requirement_references=sorted(
                invalid_requirement_refs
            ),
            invalid_acceptance_criteria_references=sorted(
                invalid_ac_refs
            ),
            orphan_normalized_scenario_ids=(
                orphan_normalized_ids
            ),
        )
    )