import json
from pathlib import Path

from agent.scenario_orchestrator import run_scenario_pipeline
from models.requirement import Requirement
from models.supplied_scenario import SuppliedScenarioCollection
from renderers.gherkin_renderer import write_feature_files
from renderers.review_report_renderer import write_review_report
from renderers.traceability_renderer import write_traceability_matrix


INPUT_FILE = Path("input/sample_scenario_requirement.json")

OUTPUT_DIRECTORY = Path("output/scenario_driven")


def main():
    print()
    print("====================================")
    print(" V&V TEST DESIGN AGENT - SCENARIO MODE")
    print("====================================")
    print()

    # ---------------------------------------------------------
    # Load and validate input
    # ---------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        input_data = json.load(file)

    project = input_data["project"]

    requirement = Requirement.model_validate(
        input_data["requirement"]
    )

    supplied_scenarios = SuppliedScenarioCollection.model_validate(
        input_data["supplied_scenarios"]
    )

    # ---------------------------------------------------------
    # Execute scenario-driven pipeline
    # ---------------------------------------------------------

    result = run_scenario_pipeline(
        project=project,
        requirement=requirement,
        supplied_scenarios=supplied_scenarios,
    )

    # ---------------------------------------------------------
    # Prepare output directory
    # ---------------------------------------------------------

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Write complete machine-readable audit package
    # ---------------------------------------------------------

    output_file = (
        OUTPUT_DIRECTORY
        / f"{requirement.requirement_id}.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            result.model_dump_json(indent=2)
        )

    # ---------------------------------------------------------
    # Write deterministic review and traceability artifacts
    # ---------------------------------------------------------

    review_report_file = write_review_report(
        package=result,
        output_directory=OUTPUT_DIRECTORY,
    )

    traceability_file = write_traceability_matrix(
        package=result,
        output_directory=OUTPUT_DIRECTORY,
    )

    # ---------------------------------------------------------
    # Generate BDD files only after successful validation
    # ---------------------------------------------------------

    feature_files = []

    if (
        result.bdd_validation.get("status") == "pass"
        and result.bdd_validation.get("valid") is True
    ):
        feature_files = write_feature_files(
            features=result.bdd_features,
            output_directory=OUTPUT_DIRECTORY,
        )

    elif result.bdd_validation.get("status") == "not_run":
        print()
        print(
            "BDD generation/validation was not run. "
            "Feature files were not generated."
        )

    else:
        print()
        print(
            "BDD validation failed. "
            "Feature files were not generated."
        )

    # ---------------------------------------------------------
    # Console summary
    # ---------------------------------------------------------

    print()
    print("------------------------------------")
    print("Scenario-driven pipeline complete")
    print("------------------------------------")

    print(
        f"Review Status: {result.review_status.value}"
    )

    print(
        f"Quality Gate: {result.quality_gate.status.value}"
    )

    print(
        f"Original Supplied Scenarios: "
        f"{len(result.supplied_scenarios.scenarios)}"
    )

    print(
        f"Source Validation: "
        f"{'PASS' if result.source_validation.valid else 'FAIL'}"
    )

    normalization_status = (
        "NOT RUN"
        if result.normalization_validation is None
        else (
            "PASS"
            if result.normalization_validation.valid
            else "FAIL"
        )
    )

    print(
        f"Normalization Validation: {normalization_status}"
    )

    print(
        f"Master Scenarios: {len(result.test_scenarios)}"
    )

    print(
        f"JAMA Test Cases: {len(result.jama_test_cases)}"
    )

    print(
        f"BDD Features: {len(result.bdd_features)}"
    )

    print(
        "AC Executable Coverage: "
        f"{result.coverage.acceptance_criteria_coverage_percent:.2f}%"
    )

    print(
        "AC Accountability: "
        f"{result.coverage.acceptance_criteria_accountability_percent:.2f}%"
    )

    print(
        f"JAMA Validation: "
        f"{result.jama_validation.get('status')}"
    )

    print(
        f"BDD Validation: "
        f"{result.bdd_validation.get('status')}"
    )

    print()
    print(f"JSON Output: {output_file}")
    print(f"Review Report: {review_report_file}")
    print(f"Traceability Matrix: {traceability_file}")

    if feature_files:
        print()
        print("Generated feature files:")

        for feature_file in feature_files:
            print(f"  - {feature_file}")

    print()


if __name__ == "__main__":
    main()