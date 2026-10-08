from agent.ambiguity_analyzer import analyze_ambiguities
from agent.bdd_generator import generate_bdd_features
from agent.bdd_validator import validate_bdd_output
from agent.coverage_analyzer import calculate_coverage
from agent.disposition_analyzer import analyze_dispositions
from agent.disposition_validator import validate_dispositions
from agent.jama_generator import generate_jama_test_cases
from agent.jama_validator import validate_jama_output
from agent.quality_gate import evaluate_quality_gate
from agent.scenario_quality_gate import (
    evaluate_scenario_quality_gate,
)
from agent.requirement_analyzer import analyze_requirement
from agent.scenario_grouper import group_scenarios
from agent.scenario_normalizer import normalize_supplied_scenarios
from agent.scenario_normalization_validator import (
    validate_scenario_normalization,
)
from agent.supplied_scenario_validator import (
    validate_supplied_scenarios,
)

from agent.orchestrator import (
    add_validation_status,
    create_not_run_validation,
    determine_review_status,
    master_coverage_passes,
)

from models.grouping import ScenarioGrouping
from models.package import ReviewStatus
from models.scenario_package import VVScenarioDesignPackageV1
from models.requirement import Requirement
from models.scenario import ScenarioCollection
from models.supplied_scenario import (
    SuppliedScenarioCollection,
)
from models.validation import ValidationStatus


def run_scenario_pipeline(
    project: str,
    requirement: Requirement,
    supplied_scenarios: SuppliedScenarioCollection,
) -> VVScenarioDesignPackageV1:
    """
    Execute the scenario-driven V&V test design pipeline.

    Human-supplied scenarios are validated and normalized
    into the canonical master scenario model before entering
    the existing coverage, grouping, JAMA and BDD pipeline.
    """

    # ---------------------------------------------------------
    # 1. Requirement analysis
    # ---------------------------------------------------------

    print("1/14 Analyzing requirement...")

    analysis = analyze_requirement(
        requirement
    )

    # ---------------------------------------------------------
    # 2. Ambiguity and gap analysis
    # ---------------------------------------------------------

    print(
        "2/14 Checking ambiguities and gaps..."
    )

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
        "3/14 Determining AC verification "
        "dispositions..."
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
        "4/14 Validating AC verification "
        "dispositions..."
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
    # 5. Validate supplied scenario source
    # ---------------------------------------------------------

    print(
        "5/14 Validating supplied scenarios..."
    )

    source_validation = (
        validate_supplied_scenarios(
            requirement=requirement,
            supplied_scenarios=(
                supplied_scenarios
            ),
        )
    )

    # ---------------------------------------------------------
    # Determine whether normalization is permitted
    # ---------------------------------------------------------

    normalization_allowed = (
        review_status != ReviewStatus.BLOCKED
        and disposition_validation.get(
            "valid",
            False,
        )
        and source_validation.valid
    )

    normalization = None
    normalization_validation = None

    # ---------------------------------------------------------
    # 6. Normalize supplied scenarios
    # ---------------------------------------------------------

    if review_status == ReviewStatus.BLOCKED:

        print(
            "Critical requirement-level finding "
            "detected. Scenario normalization "
            "is blocked."
        )

    elif not disposition_validation.get(
        "valid",
        False,
    ):

        print(
            "Verification disposition validation "
            "FAILED."
        )

        print(
            "Scenario normalization has been "
            "stopped because acceptance criterion "
            "dispositions are incomplete or invalid."
        )

    elif not source_validation.valid:

        print(
            "Supplied scenario validation FAILED."
        )

        print(
            "Scenario normalization has been "
            "stopped because the supplied scenario "
            "source contains structural or "
            "traceability errors."
        )

    else:

        print(
            "6/14 Normalizing supplied scenarios..."
        )

        normalization = (
            normalize_supplied_scenarios(
                requirement=requirement,
                analysis=analysis,
                findings=finding_collection,
                supplied_scenarios=(
                    supplied_scenarios
                ),
            )
        )

    # ---------------------------------------------------------
    # 7. Validate normalization output
    # ---------------------------------------------------------

    if normalization_allowed:

        print(
            "7/14 Validating normalized scenarios..."
        )

        normalization_validation = (
            validate_scenario_normalization(
                requirement=requirement,
                supplied_scenarios=(
                    supplied_scenarios
                ),
                normalization=normalization,
            )
        )

        if normalization_validation.valid:

            scenario_collection = (
                ScenarioCollection(
                    scenarios=(
                        normalization
                        .normalized_scenarios
                    )
                )
            )

            scenarios = (
                scenario_collection.scenarios
            )

        else:

            print(
                "Scenario normalization validation "
                "FAILED."
            )

            print(
                "Normalized scenarios will not "
                "enter downstream V&V generation."
            )

    else:

        print(
            "7/14 Normalization validation "
            "NOT RUN."
        )

    # ---------------------------------------------------------
    # Determine master scenario availability
    # ---------------------------------------------------------

    normalization_passed = (
        normalization_allowed
        and normalization_validation
        is not None
        and normalization_validation.valid
    )

    # ---------------------------------------------------------
    # 8. Master coverage analysis
    # ---------------------------------------------------------

    print(
        "8/14 Calculating master scenario "
        "coverage..."
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
        normalization_passed
        and coverage_passed
    )

    # ---------------------------------------------------------
    # 9-11. Grouping, JAMA and BDD generation
    # ---------------------------------------------------------

    if downstream_generation_allowed:

        print(
            "9/14 Grouping related scenarios..."
        )

        grouping = group_scenarios(
            requirement=requirement,
            scenarios=scenario_collection,
            findings=finding_collection,
        )

        print(
            "10/14 Generating JAMA test cases..."
        )

        jama_collection = (
            generate_jama_test_cases(
                requirement=requirement,
                scenarios=scenario_collection,
                grouping=grouping,
                findings=finding_collection,
            )
        )

        jama_test_cases = (
            jama_collection.test_cases
        )

        print(
            "11/14 Generating BDD features..."
        )

        bdd_collection = generate_bdd_features(
            requirement=requirement,
            scenarios=scenario_collection,
            findings=finding_collection,
        )

        bdd_features = (
            bdd_collection.features
        )

    else:

        if (
            normalization_passed
            and not coverage_passed
        ):

            print(
                "Master scenario coverage gate "
                "FAILED."
            )

            print(
                "JAMA and BDD generation have "
                "been stopped to prevent "
                "incomplete traceability from "
                "propagating."
            )

    # ---------------------------------------------------------
    # 12. JAMA validation
    # ---------------------------------------------------------

    if downstream_generation_allowed:

        print(
            "12/14 Validating JAMA "
            "traceability..."
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
            "12/14 JAMA validation NOT RUN."
        )

        jama_validation = create_not_run_validation(
            "JAMA generation was not executed "
            "because an upstream scenario-driven "
            "verification gate prevented "
            "downstream artifact generation."
        )

    # ---------------------------------------------------------
    # 13. BDD validation
    # ---------------------------------------------------------

    if downstream_generation_allowed:

        print(
            "13/14 Validating BDD "
            "traceability..."
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
            "13/14 BDD validation NOT RUN."
        )

        bdd_validation = create_not_run_validation(
            "BDD generation was not executed "
            "because an upstream scenario-driven "
            "verification gate prevented "
            "downstream artifact generation."
        )

    
    # ---------------------------------------------------------
    # 14. Final quality gate
    # ---------------------------------------------------------

    print(
        "14/14 Evaluating final quality gate..."
    )

    base_quality_gate = evaluate_quality_gate(
    coverage=coverage,
    findings=finding_collection.findings,
    jama_validation=jama_validation,
    bdd_validation=bdd_validation,
    )

    quality_gate = evaluate_scenario_quality_gate(
    base_quality_gate=base_quality_gate,
    source_validation=source_validation,
    normalization=normalization,
    normalization_validation=normalization_validation,
    )

    # ---------------------------------------------------------
    # Final V&V package
    #
    # The current VVDesignPackageV1 remains unchanged.
    # Scenario-specific validation evidence will be added
    # to a scenario-driven package model in a later step.
    # ---------------------------------------------------------

    return VVScenarioDesignPackageV1(
        project=project,
        supplied_scenarios=supplied_scenarios,
        source_validation=source_validation,
        normalization=normalization,
        normalization_validation=normalization_validation,
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