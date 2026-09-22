from collections import Counter

from models.grouping import ScenarioGrouping
from models.jama import JamaTestCase
from models.requirement import Requirement
from models.scenario import TestScenario


def validate_jama_output(
    requirement: Requirement,
    scenarios: list[TestScenario],
    grouping: ScenarioGrouping,
    jama_test_cases: list[JamaTestCase],
) -> dict:
    """
    Deterministically validate scenario grouping and
    JAMA test-case traceability.

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
    # Scenario grouping validation
    # ---------------------------------------------------------

    grouped_scenario_ids = [
        scenario_id
        for group in grouping.groups
        for scenario_id in group.scenario_ids
    ]

    grouped_counts = Counter(
        grouped_scenario_ids
    )

    missing_from_grouping = sorted(
        source_scenario_ids
        - set(grouped_scenario_ids)
    )

    unknown_grouped_scenarios = sorted(
        set(grouped_scenario_ids)
        - source_scenario_ids
    )

    duplicate_grouped_scenarios = sorted(
        scenario_id
        for scenario_id, count in grouped_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # JAMA scenario coverage
    # ---------------------------------------------------------

    jama_scenario_ids = [
        scenario_id
        for test_case in jama_test_cases
        for scenario_id in test_case.scenario_ids
    ]

    jama_scenario_counts = Counter(
        jama_scenario_ids
    )

    missing_from_jama = sorted(
        source_scenario_ids
        - set(jama_scenario_ids)
    )

    unknown_jama_scenarios = sorted(
        set(jama_scenario_ids)
        - source_scenario_ids
    )

    duplicate_jama_scenarios = sorted(
        scenario_id
        for scenario_id, count
        in jama_scenario_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # Test case ID validation
    # ---------------------------------------------------------

    test_case_ids = [
        test_case.test_case_id
        for test_case in jama_test_cases
    ]

    test_case_counts = Counter(
        test_case_ids
    )

    duplicate_test_case_ids = sorted(
        test_case_id
        for test_case_id, count
        in test_case_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # Requirement reference validation
    # ---------------------------------------------------------

    invalid_requirement_references = sorted(
        {
            requirement_id
            for test_case in jama_test_cases
            for requirement_id in test_case.requirement_ids
            if requirement_id not in valid_requirement_ids
        }
    )

    # ---------------------------------------------------------
    # Acceptance criterion reference validation
    # ---------------------------------------------------------

    invalid_ac_references = sorted(
        {
            ac_id
            for test_case in jama_test_cases
            for ac_id in test_case.acceptance_criteria_ids
            if ac_id not in valid_ac_ids
        }
    )

    # ---------------------------------------------------------
    # AC preservation from scenarios into JAMA
    # ---------------------------------------------------------

    scenario_ac_ids = {
        ac_id
        for scenario in scenarios
        for ac_id in scenario.acceptance_criteria_ids
    }

    jama_ac_ids = {
        ac_id
        for test_case in jama_test_cases
        for ac_id in test_case.acceptance_criteria_ids
    }

    missing_ac_from_jama = sorted(
        scenario_ac_ids
        - jama_ac_ids
    )

    # ---------------------------------------------------------
    # Group → test case count
    # ---------------------------------------------------------

    group_count = len(
        grouping.groups
    )

    test_case_count = len(
        jama_test_cases
    )

    group_test_case_count_match = (
        group_count == test_case_count
    )

    # ---------------------------------------------------------
    # Overall validity
    # ---------------------------------------------------------

    errors = []

    if missing_from_grouping:
        errors.append(
            "One or more master scenarios are missing "
            "from logical grouping."
        )

    if unknown_grouped_scenarios:
        errors.append(
            "Logical grouping contains unknown scenario IDs."
        )

    if duplicate_grouped_scenarios:
        errors.append(
            "One or more scenarios appear in multiple groups."
        )

    if missing_from_jama:
        errors.append(
            "One or more master scenarios are missing "
            "from JAMA test cases."
        )

    if unknown_jama_scenarios:
        errors.append(
            "JAMA test cases contain unknown scenario IDs."
        )

    if duplicate_jama_scenarios:
        errors.append(
            "One or more scenarios appear in multiple "
            "JAMA test cases."
        )

    if duplicate_test_case_ids:
        errors.append(
            "Duplicate JAMA test case IDs were detected."
        )

    if invalid_requirement_references:
        errors.append(
            "Invalid requirement references were detected."
        )

    if invalid_ac_references:
        errors.append(
            "Invalid acceptance criterion references "
            "were detected."
        )

    if missing_ac_from_jama:
        errors.append(
            "Acceptance criterion traceability was lost "
            "between master scenarios and JAMA test cases."
        )

    if not group_test_case_count_match:
        errors.append(
            "Logical group count does not match JAMA "
            "test case count."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "missing_from_grouping": missing_from_grouping,
        "unknown_grouped_scenarios": (
            unknown_grouped_scenarios
        ),
        "duplicate_grouped_scenarios": (
            duplicate_grouped_scenarios
        ),
        "missing_from_jama": missing_from_jama,
        "unknown_jama_scenarios": (
            unknown_jama_scenarios
        ),
        "duplicate_jama_scenarios": (
            duplicate_jama_scenarios
        ),
        "duplicate_test_case_ids": (
            duplicate_test_case_ids
        ),
        "invalid_requirement_references": (
            invalid_requirement_references
        ),
        "invalid_ac_references": (
            invalid_ac_references
        ),
        "missing_ac_from_jama": (
            missing_ac_from_jama
        ),
        "group_count": group_count,
        "test_case_count": test_case_count,
        "group_test_case_count_match": (
            group_test_case_count_match
        ),
    }