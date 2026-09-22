from collections import Counter

from models.coverage import (
    AcceptanceCriterionCoverage,
    CoverageAnalysis,
    RequirementCoverage,
)
from models.disposition import (
    DispositionCollection,
    VerificationDisposition,
)
from models.requirement import Requirement
from models.scenario import TestScenario


def calculate_coverage(
    requirement: Requirement,
    scenarios: list[TestScenario],
    dispositions: DispositionCollection | None = None,
) -> CoverageAnalysis:
    """
    Deterministically calculate requirement and acceptance
    criterion coverage.

    The analysis distinguishes between:

    1. Executable coverage:
       An AC is mapped to at least one master scenario.

    2. Accountability:
       An AC has a valid verification disposition, including
       BLOCKED ACs for which no defensible executable scenario
       can be generated.

    No AI model is used.
    """

    valid_requirement_ids = {
        requirement.requirement_id
    }

    valid_ac_ids = {
        ac.id
        for ac in requirement.acceptance_criteria
    }

    # ---------------------------------------------------------
    # Build disposition map
    # ---------------------------------------------------------

    disposition_map = {}

    if dispositions is not None:
        disposition_map = {
            item.acceptance_criterion_id: item.disposition
            for item in dispositions.dispositions
        }

    # ---------------------------------------------------------
    # Duplicate scenario IDs
    # ---------------------------------------------------------

    scenario_id_counts = Counter(
        scenario.scenario_id
        for scenario in scenarios
    )

    duplicate_scenario_ids = sorted(
        scenario_id
        for scenario_id, count
        in scenario_id_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # Requirement mapping
    # ---------------------------------------------------------

    requirement_to_scenarios = {
        requirement_id: []
        for requirement_id in valid_requirement_ids
    }

    # ---------------------------------------------------------
    # AC mapping
    # ---------------------------------------------------------

    ac_to_scenarios = {
        ac_id: []
        for ac_id in valid_ac_ids
    }

    invalid_requirement_references = set()
    invalid_ac_references = set()
    orphan_scenario_ids = []

    # ---------------------------------------------------------
    # Analyze scenario traceability
    # ---------------------------------------------------------

    for scenario in scenarios:

        has_valid_requirement_reference = False

        for requirement_id in scenario.requirement_ids:

            if requirement_id in valid_requirement_ids:
                requirement_to_scenarios[
                    requirement_id
                ].append(
                    scenario.scenario_id
                )

                has_valid_requirement_reference = True

            else:
                invalid_requirement_references.add(
                    requirement_id
                )

        for ac_id in scenario.acceptance_criteria_ids:

            if ac_id in valid_ac_ids:
                ac_to_scenarios[
                    ac_id
                ].append(
                    scenario.scenario_id
                )

            else:
                invalid_ac_references.add(
                    ac_id
                )

        if not has_valid_requirement_reference:
            orphan_scenario_ids.append(
                scenario.scenario_id
            )

    # ---------------------------------------------------------
    # Requirement coverage
    # ---------------------------------------------------------

    requirement_coverage = []

    for requirement_id in sorted(
        valid_requirement_ids
    ):
        scenario_ids = sorted(
            set(
                requirement_to_scenarios[
                    requirement_id
                ]
            )
        )

        requirement_coverage.append(
            RequirementCoverage(
                requirement_id=requirement_id,
                scenario_ids=scenario_ids,
                covered=bool(scenario_ids),
            )
        )

    uncovered_requirement_ids = [
        item.requirement_id
        for item in requirement_coverage
        if not item.covered
    ]

    # ---------------------------------------------------------
    # Acceptance criterion coverage and accountability
    # ---------------------------------------------------------

    acceptance_criteria_coverage = []

    uncovered_ac_ids = []
    unaccounted_ac_ids = []
    blocked_ac_ids = []

    for ac_id in sorted(valid_ac_ids):

        scenario_ids = sorted(
            set(
                ac_to_scenarios[
                    ac_id
                ]
            )
        )

        disposition = disposition_map.get(
            ac_id
        )

        executable = bool(scenario_ids)

        accounted_for = (
            disposition is not None
        )

        if (
            disposition
            == VerificationDisposition.BLOCKED
        ):
            blocked_ac_ids.append(ac_id)

        if not executable:
            uncovered_ac_ids.append(ac_id)

        if not accounted_for:
            unaccounted_ac_ids.append(ac_id)

        acceptance_criteria_coverage.append(
            AcceptanceCriterionCoverage(
                acceptance_criterion_id=ac_id,
                scenario_ids=scenario_ids,
                disposition=(
                    disposition.value
                    if disposition is not None
                    else None
                ),
                covered=executable,
                accounted_for=accounted_for,
                executable=executable,
            )
        )

    # ---------------------------------------------------------
    # Percentages
    # ---------------------------------------------------------

    total_requirements = len(
        requirement_coverage
    )

    covered_requirements = sum(
        1
        for item in requirement_coverage
        if item.covered
    )

    if total_requirements:
        requirement_coverage_percent = round(
            (
                covered_requirements
                / total_requirements
            )
            * 100,
            2,
        )
    else:
        requirement_coverage_percent = 100.0

    total_acs = len(
        acceptance_criteria_coverage
    )

    executable_acs = sum(
        1
        for item in acceptance_criteria_coverage
        if item.executable
    )

    accounted_acs = sum(
        1
        for item in acceptance_criteria_coverage
        if item.accounted_for
    )

    if total_acs:
        ac_coverage_percent = round(
            (
                executable_acs
                / total_acs
            )
            * 100,
            2,
        )

        ac_accountability_percent = round(
            (
                accounted_acs
                / total_acs
            )
            * 100,
            2,
        )

    else:
        ac_coverage_percent = 100.0
        ac_accountability_percent = 100.0

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    return CoverageAnalysis(
        requirement_coverage=(
            requirement_coverage
        ),
        acceptance_criteria_coverage=(
            acceptance_criteria_coverage
        ),
        uncovered_requirement_ids=(
            sorted(
                uncovered_requirement_ids
            )
        ),
        uncovered_acceptance_criteria_ids=(
            sorted(
                uncovered_ac_ids
            )
        ),
        unaccounted_acceptance_criteria_ids=(
            sorted(
                unaccounted_ac_ids
            )
        ),
        blocked_acceptance_criteria_ids=(
            sorted(
                blocked_ac_ids
            )
        ),
        orphan_scenario_ids=sorted(
            set(orphan_scenario_ids)
        ),
        invalid_requirement_references=sorted(
            invalid_requirement_references
        ),
        invalid_acceptance_criteria_references=sorted(
            invalid_ac_references
        ),
        duplicate_scenario_ids=(
            duplicate_scenario_ids
        ),
        requirement_coverage_percent=(
            requirement_coverage_percent
        ),
        acceptance_criteria_coverage_percent=(
            ac_coverage_percent
        ),
        acceptance_criteria_accountability_percent=(
            ac_accountability_percent
        ),
    )