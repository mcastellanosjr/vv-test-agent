from agent.ambiguity_analyzer import analyze_ambiguities
from agent.bdd_generator import generate_bdd_features
from agent.bdd_validator import validate_bdd_output
from agent.coverage_analyzer import calculate_coverage
from agent.disposition_analyzer import analyze_dispositions
from agent.disposition_validator import validate_dispositions
from agent.jama_generator import generate_jama_test_cases
from agent.jama_validator import validate_jama_output
from agent.quality_gate import evaluate_quality_gate
from agent.requirement_analyzer import analyze_requirement
from agent.scenario_generator import generate_scenarios
from agent.scenario_grouper import group_scenarios

from models.finding import FindingSeverity
from models.grouping import ScenarioGrouping
from models.package import ReviewStatus, VVDesignPackageV1
from models.requirement import Requirement
from models.scenario import ScenarioCollection
from models.validation import ValidationStatus


def determine_review_status(findings):
    """
    Determine the requirement-level review status
    using deterministic severity rules.
    """

    severities = {
        finding.severity
        for finding in findings
    }

    if FindingSeverity.CRITICAL in severities:
        return ReviewStatus.BLOCKED

    if (
        FindingSeverity.HIGH in severities
        or FindingSeverity.MEDIUM in severities
    ):
        return ReviewStatus.REVIEW_RECOMMENDED

    return ReviewStatus.READY


def master_coverage_passes(coverage) -> bool:
    """
    Determine whether the master scenario design is
    structurally acceptable for downstream generation.

    TESTABLE and LIMITED acceptance criteria require
    executable scenario coverage.

    BLOCKED acceptance criteria are explicitly accounted for
    by their verification disposition and do not require an
    invented executable scenario.
    """

    non_blocked_uncovered_acs = [
        ac_id
        for ac_id
        in coverage.uncovered_acceptance_criteria_ids
        if ac_id
        not in coverage.blocked_acceptance_criteria_ids
    ]

    return (
        not coverage.uncovered_requirement_ids
        and not non_blocked_uncovered_acs
        and not coverage.unaccounted_acceptance_criteria_ids
        and not coverage.orphan_scenario_ids
        and not coverage.invalid_requirement_references
        and not coverage.invalid_acceptance_criteria_references
        and not coverage.duplicate_scenario_ids
    )


def create_not_run_validation(reason: str) -> dict:
    """
    Create a deterministic validation result for a stage that
    was intentionally not executed because an upstream gate
    prevented downstream artifact generation.
    """

    return {
        "status": ValidationStatus.NOT_RUN.value,
        "valid": None,
        "errors": [],
        "reason": reason,
    }


def add_validation_status(validation: dict) -> dict:
    """
    Add an explicit PASS or FAIL status to an existing
    validator result.
    """

    result = dict(validation)

    if result.get("valid", False):
        result["status"] = ValidationStatus.PASS.value
    else:
        result["status"] = ValidationStatus.FAIL.value

    return result


def run_pipeline(
    project: str,
    requirement: Requirement,
) -> VVDesignPackageV1:
    """
    Execute the complete V&V test design pipeline.
    """

    # ---------------------------------------------------------
    # 1. Requirement analysis
    # ---------------------------------------------------------

    print("1/12 Analyzing requirement...")

    analysis = analyze_requirement(
        requirement
    )

    # ---------------------------------------------------------
    # 2. Ambiguity and gap analysis
    # ---------------------------------------------------------

    print("2/12 Checking ambiguities and gaps...")

    finding_collection = analyze_ambiguities(
        requirement,
        analysis,
    )

    review_status = determine_review_status(
        finding_collection.findings
    )

    # ---------------------------------------------------------
    # 3. AC verification dispositions
    # ---------------------------------------------------------

    print(
        "3/12 Determining AC verification dispositions..."
    )

    disposition_collection = analyze_dispositions(
        requirement=requirement,
        analysis=analysis,
        findings=finding_collection,
    )

    # ---------------------------------------------------------
    # 4. Disposition validation
    # ---------------------------------------------------------

    print(
        "4/12 Validating AC verification dispositions..."
    )

    disposition_validation = validate_dispositions(
        requirement=requirement,
        dispositions=disposition_collection,
        findings=finding_collection,
    )

    # ---------------------------------------------------------
    # Initialize downstream artifacts
    # ---------------------------------------------------------

    scenarios = []

    scenario_collection = ScenarioCollection(
        scenarios=[]
    )

    grouping = ScenarioGrouping(
        groups=[]
    )

    jama_test_cases = []
    bdd_features = []

    # ---------------------------------------------------------
    # 5. Master scenario generation
    # ---------------------------------------------------------

    scenario_generation_allowed = (
        review_status != ReviewStatus.BLOCKED
        and disposition_validation.get(
            "valid",
            False,
        )
    )

    if review_status == ReviewStatus.BLOCKED:

        print(
            "Critical requirement-level finding detected. "
            "Master scenario generation is blocked."
        )

    elif not disposition_validation.get(
        "valid",
        False,
    ):

        print(
            "Verification disposition validation FAILED."
        )

        print(
            "Master scenario generation has been stopped "
            "because acceptance criterion dispositions "
            "are incomplete or invalid."
        )

    else:

        print(
            "5/12 Generating master test scenarios..."
        )

        scenario_collection = generate_scenarios(
            requirement=requirement,
            analysis=analysis,
            findings=finding_collection,
            dispositions=disposition_collection,
        )

        scenarios = scenario_collection.scenarios

    # ---------------------------------------------------------
    # 6. Master coverage analysis
    # ---------------------------------------------------------

    print(
        "6/12 Calculating master scenario coverage..."
    )

    coverage = calculate_coverage(
        requirement=requirement,
        scenarios=scenarios,
        dispositions=disposition_collection,
    )

    coverage_passed = master_coverage_passes(
        coverage
    )

    # ---------------------------------------------------------
    # Determine whether downstream generation is permitted
    # ---------------------------------------------------------

    downstream_generation_allowed = (
        scenario_generation_allowed
        and coverage_passed
    )

    # ---------------------------------------------------------
    # 7-9. Grouping, JAMA, BDD generation
    # ---------------------------------------------------------

    if downstream_generation_allowed:

        print(
            "7/12 Grouping related scenarios..."
        )

        grouping = group_scenarios(
            requirement=requirement,
            scenarios=scenario_collection,
            findings=finding_collection,
        )

        print(
            "8/12 Generating JAMA test cases..."
        )

        jama_collection = generate_jama_test_cases(
            requirement=requirement,
            scenarios=scenario_collection,
            grouping=grouping,
            findings=finding_collection,
        )

        jama_test_cases = (
            jama_collection.test_cases
        )

        print(
            "9/12 Generating BDD features..."
        )

        bdd_collection = generate_bdd_features(
            requirement=requirement,
            scenarios=scenario_collection,
            findings=finding_collection,
        )

        bdd_features = bdd_collection.features

    else:

        if (
            scenario_generation_allowed
            and not coverage_passed
        ):
            print(
                "Master scenario coverage gate FAILED."
            )

            print(
                "JAMA and BDD generation have been "
                "stopped to prevent incomplete "
                "traceability from propagating."
            )

    # ---------------------------------------------------------
    # 10. JAMA validation
    # ---------------------------------------------------------

    if downstream_generation_allowed:

        print(
            "10/12 Validating JAMA traceability..."
        )

        jama_validation = validate_jama_output(
            requirement=requirement,
            scenarios=scenarios,
            grouping=grouping,
            jama_test_cases=jama_test_cases,
        )

        jama_validation = add_validation_status(
            jama_validation
        )

    else:

        print(
            "10/12 JAMA validation NOT RUN."
        )

        jama_validation = create_not_run_validation(
            "JAMA generation was not executed because "
            "an upstream verification gate prevented "
            "downstream artifact generation."
        )

    # ---------------------------------------------------------
    # 11. BDD validation
    # ---------------------------------------------------------

    if downstream_generation_allowed:

        print(
            "11/12 Validating BDD traceability..."
        )

        bdd_validation = validate_bdd_output(
            requirement=requirement,
            scenarios=scenarios,
            bdd_features=bdd_features,
        )

        bdd_validation = add_validation_status(
            bdd_validation
        )

    else:

        print(
            "11/12 BDD validation NOT RUN."
        )

        bdd_validation = create_not_run_validation(
            "BDD generation was not executed because "
            "an upstream verification gate prevented "
            "downstream artifact generation."
        )

    # ---------------------------------------------------------
    # 12. Final quality gate
    # ---------------------------------------------------------

    print(
        "12/12 Evaluating final quality gate..."
    )

    quality_gate = evaluate_quality_gate(
        coverage=coverage,
        findings=finding_collection.findings,
        jama_validation=jama_validation,
        bdd_validation=bdd_validation,
    )

    # ---------------------------------------------------------
    # Final V&V package
    # ---------------------------------------------------------

    return VVDesignPackageV1(
        project=project,
        requirement=requirement,
        analysis=analysis,
        findings=finding_collection.findings,
        review_status=review_status,
        verification_dispositions=(
            disposition_collection.dispositions
        ),
        disposition_validation=(
            disposition_validation
        ),
        test_scenarios=scenarios,
        coverage=coverage,
        scenario_grouping=grouping,
        jama_test_cases=jama_test_cases,
        jama_validation=jama_validation,
        bdd_features=bdd_features,
        bdd_validation=bdd_validation,
        quality_gate=quality_gate,
    )