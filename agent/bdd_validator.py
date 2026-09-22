from collections import Counter

from models.bdd import BDDFeature
from models.requirement import Requirement
from models.scenario import TestScenario


def validate_bdd_output(
    requirement: Requirement,
    scenarios: list[TestScenario],
    bdd_features: list[BDDFeature],
) -> dict:
    """
    Deterministically validate BDD traceability and structure.

    No AI model is used.
    """

    source_scenario_ids = {
        scenario.scenario_id
        for scenario in scenarios
    }

    valid_requirement_ids = {
        requirement.requirement_id
    }

    valid_ac_ids = {
        ac.id
        for ac in requirement.acceptance_criteria
    }

    # ---------------------------------------------------------
    # Feature ID validation
    # ---------------------------------------------------------

    feature_ids = [
        feature.feature_id
        for feature in bdd_features
    ]

    feature_id_counts = Counter(
        feature_ids
    )

    duplicate_feature_ids = sorted(
        feature_id
        for feature_id, count
        in feature_id_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # BDD scenario ID validation
    # ---------------------------------------------------------

    all_bdd_scenarios = [
        bdd_scenario
        for feature in bdd_features
        for bdd_scenario in feature.scenarios
    ]

    bdd_scenario_ids = [
        scenario.scenario_id
        for scenario in all_bdd_scenarios
    ]

    bdd_scenario_id_counts = Counter(
        bdd_scenario_ids
    )

    duplicate_bdd_scenario_ids = sorted(
        scenario_id
        for scenario_id, count
        in bdd_scenario_id_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # Master scenario preservation
    # ---------------------------------------------------------

    referenced_master_scenario_ids = [
        master_scenario_id
        for bdd_scenario in all_bdd_scenarios
        for master_scenario_id
        in bdd_scenario.master_scenario_ids
    ]

    referenced_master_counts = Counter(
        referenced_master_scenario_ids
    )

    missing_master_scenarios = sorted(
        source_scenario_ids
        - set(referenced_master_scenario_ids)
    )

    unknown_master_scenarios = sorted(
        set(referenced_master_scenario_ids)
        - source_scenario_ids
    )

    duplicate_master_scenario_mappings = sorted(
        scenario_id
        for scenario_id, count
        in referenced_master_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # Requirement reference validation
    # ---------------------------------------------------------

    invalid_requirement_references = sorted(
        {
            requirement_id
            for bdd_scenario in all_bdd_scenarios
            for requirement_id
            in bdd_scenario.requirement_ids
            if requirement_id not in valid_requirement_ids
        }
    )

    # Also validate feature-level requirement references.

    invalid_feature_requirement_references = sorted(
        {
            requirement_id
            for feature in bdd_features
            for requirement_id in feature.requirement_ids
            if requirement_id not in valid_requirement_ids
        }
    )

    # ---------------------------------------------------------
    # Acceptance criterion reference validation
    # ---------------------------------------------------------

    invalid_ac_references = sorted(
        {
            ac_id
            for bdd_scenario in all_bdd_scenarios
            for ac_id
            in bdd_scenario.acceptance_criteria_ids
            if ac_id not in valid_ac_ids
        }
    )

    # ---------------------------------------------------------
    # AC preservation
    # ---------------------------------------------------------

    source_ac_ids = {
        ac_id
        for scenario in scenarios
        for ac_id in scenario.acceptance_criteria_ids
    }

    bdd_ac_ids = {
        ac_id
        for bdd_scenario in all_bdd_scenarios
        for ac_id in bdd_scenario.acceptance_criteria_ids
    }

    missing_ac_from_bdd = sorted(
        source_ac_ids
        - bdd_ac_ids
    )

    # ---------------------------------------------------------
    # Orphan BDD scenarios
    # ---------------------------------------------------------

    orphan_bdd_scenario_ids = sorted(
        bdd_scenario.scenario_id
        for bdd_scenario in all_bdd_scenarios
        if (
            not bdd_scenario.master_scenario_ids
            or not bdd_scenario.requirement_ids
        )
    )

    # ---------------------------------------------------------
    # Empty Given / When / Then detection
    # ---------------------------------------------------------

    empty_given_scenarios = sorted(
        scenario.scenario_id
        for scenario in all_bdd_scenarios
        if not scenario.given
    )

    empty_when_scenarios = sorted(
        scenario.scenario_id
        for scenario in all_bdd_scenarios
        if not scenario.when
    )

    empty_then_scenarios = sorted(
        scenario.scenario_id
        for scenario in all_bdd_scenarios
        if not scenario.then
    )

    # ---------------------------------------------------------
    # Overall validation
    # ---------------------------------------------------------

    errors = []

    if duplicate_feature_ids:
        errors.append(
            "Duplicate BDD feature IDs were detected."
        )

    if duplicate_bdd_scenario_ids:
        errors.append(
            "Duplicate BDD scenario IDs were detected."
        )

    if missing_master_scenarios:
        errors.append(
            "One or more master scenarios are missing "
            "from BDD coverage."
        )

    if unknown_master_scenarios:
        errors.append(
            "BDD output contains unknown master scenario IDs."
        )

    if duplicate_master_scenario_mappings:
        errors.append(
            "One or more master scenarios are mapped to "
            "multiple BDD scenarios."
        )

    if invalid_requirement_references:
        errors.append(
            "Invalid requirement references were detected "
            "in BDD scenarios."
        )

    if invalid_feature_requirement_references:
        errors.append(
            "Invalid requirement references were detected "
            "at BDD feature level."
        )

    if invalid_ac_references:
        errors.append(
            "Invalid acceptance criterion references were "
            "detected in BDD scenarios."
        )

    if missing_ac_from_bdd:
        errors.append(
            "Acceptance criterion traceability was lost "
            "between master scenarios and BDD scenarios."
        )

    if orphan_bdd_scenario_ids:
        errors.append(
            "One or more BDD scenarios are missing master "
            "scenario or requirement traceability."
        )

    if empty_given_scenarios:
        errors.append(
            "One or more BDD scenarios have no GIVEN state."
        )

    if empty_when_scenarios:
        errors.append(
            "One or more BDD scenarios have no WHEN behavior."
        )

    if empty_then_scenarios:
        errors.append(
            "One or more BDD scenarios have no THEN result."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "missing_master_scenarios": (
            missing_master_scenarios
        ),
        "unknown_master_scenarios": (
            unknown_master_scenarios
        ),
        "duplicate_master_scenario_mappings": (
            duplicate_master_scenario_mappings
        ),
        "duplicate_feature_ids": (
            duplicate_feature_ids
        ),
        "duplicate_bdd_scenario_ids": (
            duplicate_bdd_scenario_ids
        ),
        "invalid_requirement_references": (
            invalid_requirement_references
        ),
        "invalid_feature_requirement_references": (
            invalid_feature_requirement_references
        ),
        "invalid_ac_references": (
            invalid_ac_references
        ),
        "missing_ac_from_bdd": (
            missing_ac_from_bdd
        ),
        "orphan_bdd_scenario_ids": (
            orphan_bdd_scenario_ids
        ),
        "empty_given_scenarios": (
            empty_given_scenarios
        ),
        "empty_when_scenarios": (
            empty_when_scenarios
        ),
        "empty_then_scenarios": (
            empty_then_scenarios
        ),
        "feature_count": len(
            bdd_features
        ),
        "bdd_scenario_count": len(
            all_bdd_scenarios
        ),
        "master_scenario_count": len(
            scenarios
        ),
    }