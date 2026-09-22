import json
from pathlib import Path

from agent.orchestrator import run_pipeline
from models.requirement import Requirement
from renderers.gherkin_renderer import write_feature_files
from renderers.review_report_renderer import write_review_report
from renderers.traceability_renderer import write_traceability_matrix

INPUT_FILE = Path(
    "input/sample_requirement.json"
)

OUTPUT_DIRECTORY = Path(
    "output"
)


def main():
    print()
    print(
        "===================================="
    )
    print(
        " V&V TEST DESIGN AGENT - V1"
    )
    print(
        "===================================="
    )
    print()

    # ---------------------------------------------------------
    # Load input
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

    # ---------------------------------------------------------
    # Execute pipeline
    # ---------------------------------------------------------

    result = run_pipeline(
        project=project,
        requirement=requirement,
    )

    # ---------------------------------------------------------
    # Prepare output directory
    # ---------------------------------------------------------

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Write complete machine-readable package
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
            result.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Write deterministic human-readable review report
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
    # Write BDD feature files only when BDD validation passed
    # ---------------------------------------------------------

    feature_files = []

    if (
        result.bdd_validation.get("status")
        == "pass"
        and result.bdd_validation.get("valid")
        is True
    ):
        feature_files = write_feature_files(
            features=result.bdd_features,
            output_directory=OUTPUT_DIRECTORY,
        )

    elif (
        result.bdd_validation.get("status")
        == "not_run"
    ):
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
    print(
        "------------------------------------"
    )
    print(
        "Pipeline complete"
    )
    print(
        "------------------------------------"
    )

    print(
        "Review Status: "
        f"{result.review_status.value}"
    )

    print(
        "Quality Gate: "
        f"{result.quality_gate.status.value}"
    )

    print(
        f"Findings: {len(result.findings)}"
    )

    print(
        "Test Scenarios: "
        f"{len(result.test_scenarios)}"
    )

    print(
        "JAMA Test Cases: "
        f"{len(result.jama_test_cases)}"
    )

    print(
        "BDD Features: "
        f"{len(result.bdd_features)}"
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
        "JAMA Validation: "
        f"{result.jama_validation.get('status')}"
    )

    print(
        "BDD Validation: "
        f"{result.bdd_validation.get('status')}"
    )

    print()
    print(
        f"JSON Output: {output_file}"
    )

    print(
        "Review Report: "
        f"{review_report_file}"
    )

    print(
        "Traceability Matrix: "
    f"{traceability_file}"
    )

    if feature_files:
        print()
        print(
            "Generated feature files:"
        )

        for feature_file in feature_files:
            print(
                f"  - {feature_file}"
            )

    print()


if __name__ == "__main__":
    main()