from agent.coverage_analyzer import calculate_coverage
from models.disposition import (
    AcceptanceCriterionDisposition,
    DispositionCollection,
    VerificationDisposition,
)
from models.requirement import (
    AcceptanceCriterion,
    Requirement,
)
from models.scenario import (
    TestScenario as VVTestScenario,
    TestType as VVTestType,
)


def build_requirement():
    return Requirement(
        requirement_id="REQ-001",
        title="Test Requirement",
        text="The system shall perform the required behavior.",
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-01",
                text="Behavior one shall occur.",
            ),
            AcceptanceCriterion(
                id="AC-02",
                text="Behavior two shall occur.",
            ),
            AcceptanceCriterion(
                id="AC-03",
                text="Behavior three shall occur.",
            ),
        ],
    )


def build_dispositions(
    ac02_disposition=VerificationDisposition.LIMITED,
):
    return DispositionCollection(
        dispositions=[
            AcceptanceCriterionDisposition(
                acceptance_criterion_id="AC-01",
                disposition=VerificationDisposition.TESTABLE,
                rationale="Sufficiently defined.",
                supported_behavior=["Behavior one."],
            ),
            AcceptanceCriterionDisposition(
                acceptance_criterion_id="AC-02",
                disposition=ac02_disposition,
                rationale="Disposition for AC-02.",
                supported_behavior=["Behavior two."],
            ),
            AcceptanceCriterionDisposition(
                acceptance_criterion_id="AC-03",
                disposition=VerificationDisposition.TESTABLE,
                rationale="Sufficiently defined.",
                supported_behavior=["Behavior three."],
            ),
        ]
    )


def build_scenario(
    scenario_id,
    ac_ids,
):
    return VVTestScenario(
        scenario_id=scenario_id,
        title=f"Scenario {scenario_id}",
        objective="Verify supported behavior.",
        test_type=VVTestType.HAPPY_PATH,
        preconditions=[],
        actions=["Perform the supported action."],
        expected_behavior=[
            "The supported behavior occurs."
        ],
        requirement_ids=["REQ-001"],
        acceptance_criteria_ids=ac_ids,
    )


def test_complete_ac_coverage_and_accountability():
    requirement = build_requirement()

    dispositions = build_dispositions()

    scenarios = [
        build_scenario("TS-001", ["AC-01"]),
        build_scenario("TS-002", ["AC-02"]),
        build_scenario("TS-003", ["AC-03"]),
    ]

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=dispositions,
    )

    assert (
        coverage.requirement_coverage_percent
        == 100.0
    )

    assert (
        coverage.acceptance_criteria_coverage_percent
        == 100.0
    )

    assert (
        coverage.acceptance_criteria_accountability_percent
        == 100.0
    )

    assert (
        coverage.uncovered_acceptance_criteria_ids
        == []
    )

    assert (
        coverage.unaccounted_acceptance_criteria_ids
        == []
    )


def test_missing_limited_ac_is_uncovered():
    requirement = build_requirement()

    dispositions = build_dispositions()

    scenarios = [
        build_scenario("TS-001", ["AC-01"]),
        build_scenario("TS-003", ["AC-03"]),
    ]

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=dispositions,
    )

    assert "AC-02" in (
        coverage.uncovered_acceptance_criteria_ids
    )

    assert (
        coverage.acceptance_criteria_coverage_percent
        == 66.67
    )

    # It still has a disposition, so it remains accounted for.
    assert (
        coverage.acceptance_criteria_accountability_percent
        == 100.0
    )


def test_blocked_ac_is_visible_without_scenario():
    requirement = build_requirement()

    dispositions = build_dispositions(
        ac02_disposition=(
            VerificationDisposition.BLOCKED
        )
    )

    scenarios = [
        build_scenario("TS-001", ["AC-01"]),
        build_scenario("TS-003", ["AC-03"]),
    ]

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=dispositions,
    )

    assert "AC-02" in (
        coverage.blocked_acceptance_criteria_ids
    )

    assert "AC-02" in (
        coverage.uncovered_acceptance_criteria_ids
    )

    assert (
        coverage.acceptance_criteria_coverage_percent
        == 66.67
    )

    assert (
        coverage.acceptance_criteria_accountability_percent
        == 100.0
    )


def test_missing_disposition_is_unaccounted():
    requirement = build_requirement()

    dispositions = DispositionCollection(
        dispositions=[
            AcceptanceCriterionDisposition(
                acceptance_criterion_id="AC-01",
                disposition=VerificationDisposition.TESTABLE,
                rationale="Defined.",
                supported_behavior=["Behavior one."],
            ),
            AcceptanceCriterionDisposition(
                acceptance_criterion_id="AC-03",
                disposition=VerificationDisposition.TESTABLE,
                rationale="Defined.",
                supported_behavior=["Behavior three."],
            ),
        ]
    )

    scenarios = [
        build_scenario("TS-001", ["AC-01"]),
        build_scenario("TS-003", ["AC-03"]),
    ]

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=dispositions,
    )

    assert "AC-02" in (
        coverage.unaccounted_acceptance_criteria_ids
    )

    assert (
        coverage.acceptance_criteria_accountability_percent
        == 66.67
    )


def test_invalid_ac_reference_is_detected():
    requirement = build_requirement()

    dispositions = build_dispositions()

    scenarios = [
        build_scenario(
            "TS-001",
            ["AC-01", "AC-999"],
        )
    ]

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=dispositions,
    )

    assert "AC-999" in (
        coverage.invalid_acceptance_criteria_references
    )


def test_duplicate_scenario_id_is_detected():
    requirement = build_requirement()

    dispositions = build_dispositions()

    scenarios = [
        build_scenario("TS-001", ["AC-01"]),
        build_scenario("TS-001", ["AC-02"]),
    ]

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=dispositions,
    )

    assert "TS-001" in (
        coverage.duplicate_scenario_ids
    )