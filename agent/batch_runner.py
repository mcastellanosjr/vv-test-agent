import json
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from agent.orchestrator import run_pipeline

from models.batch import (
    BatchItemStatus,
    BatchRequirementResult,
    BatchSummary,
)
from models.disposition import VerificationDisposition
from models.quality import QualityGateStatus
from models.requirement import Requirement

from renderers.gherkin_renderer import write_feature_files
from renderers.review_report_renderer import write_review_report
from renderers.traceability_renderer import write_traceability_matrix


def create_run_id() -> str:
    """
    Create a readable identifier for one batch execution.

    Example:
        20260923-143501
    """

    return datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )


def discover_requirement_files(
    input_directory: Path,
) -> list[Path]:
    """
    Discover JSON requirement files in deterministic
    filename order.

    Only files directly inside the supplied directory
    are included.
    """

    if not input_directory.exists():
        raise FileNotFoundError(
            "Batch input directory does not exist: "
            f"{input_directory}"
        )

    if not input_directory.is_dir():
        raise NotADirectoryError(
            "Batch input path is not a directory: "
            f"{input_directory}"
        )

    return sorted(
        [
            path
            for path in input_directory.iterdir()
            if (
                path.is_file()
                and path.suffix.lower() == ".json"
            )
        ],
        key=lambda path: path.name.lower(),
    )


def count_bdd_scenarios(package) -> int:
    """
    Count all BDD scenarios in a generated package.
    """

    return sum(
        len(feature.scenarios)
        for feature in package.bdd_features
    )


def count_dispositions(
    package,
    target: VerificationDisposition,
) -> int:
    """
    Count AC verification dispositions of a given type.
    """

    return sum(
        1
        for disposition
        in package.verification_dispositions
        if disposition.disposition == target
    )


def map_quality_status(
    quality_status: QualityGateStatus,
) -> BatchItemStatus:
    """
    Convert the requirement-level quality gate status
    into a batch item status.
    """

    if quality_status == QualityGateStatus.PASS:
        return BatchItemStatus.PASS

    if quality_status == QualityGateStatus.REVIEW:
        return BatchItemStatus.REVIEW

    return BatchItemStatus.FAIL


def write_package_json(
    package,
    output_directory: Path,
) -> Path:
    """
    Write the complete machine-readable V&V package.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / (
            f"{package.requirement.requirement_id}"
            ".json"
        )
    )

    output_path.write_text(
        package.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    return output_path


def process_requirement_file(
    input_file: Path,
    project: str,
    run_output_directory: Path,
) -> BatchRequirementResult:
    """
    Process one requirement file.

    Errors are captured and converted into an ERROR result
    so that processing of other requirements can continue.
    """

    requirement_id = input_file.stem
    requirement_title = None

    try:
        # -----------------------------------------------------
        # Load JSON
        # -----------------------------------------------------

        with input_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            input_data = json.load(file)

        # -----------------------------------------------------
        # Support either:
        #
        # {
        #   "project": "...",
        #   "requirement": {...}
        # }
        #
        # or a direct Requirement object:
        #
        # {
        #   "requirement_id": "...",
        #   ...
        # }
        # -----------------------------------------------------

        if (
            isinstance(input_data, dict)
            and "requirement" in input_data
        ):
            requirement_data = (
                input_data["requirement"]
            )

            file_project = input_data.get(
                "project",
                project,
            )
        else:
            requirement_data = input_data
            file_project = project

        # -----------------------------------------------------
        # Validate requirement input
        # -----------------------------------------------------

        requirement = Requirement.model_validate(
            requirement_data
        )

        requirement_id = (
            requirement.requirement_id
        )

        requirement_title = (
            requirement.title
        )

        # -----------------------------------------------------
        # Create isolated requirement output directory
        # -----------------------------------------------------

        requirement_output_directory = (
            run_output_directory
            / requirement.requirement_id
        )

        requirement_output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------------------
        # Execute existing stable V&V pipeline
        # -----------------------------------------------------

        package = run_pipeline(
            project=file_project,
            requirement=requirement,
        )

        # -----------------------------------------------------
        # Write deterministic artifacts
        # -----------------------------------------------------

        json_output = write_package_json(
            package=package,
            output_directory=(
                requirement_output_directory
            ),
        )

        review_report = write_review_report(
            package=package,
            output_directory=(
                requirement_output_directory
            ),
        )

        traceability_matrix = (
            write_traceability_matrix(
                package=package,
                output_directory=(
                    requirement_output_directory
                ),
            )
        )

        # -----------------------------------------------------
        # Write feature files only when BDD validation passes
        # -----------------------------------------------------

        feature_files = []

        if (
            package.bdd_validation.get(
                "status"
            )
            == "pass"
            and package.bdd_validation.get(
                "valid"
            )
            is True
        ):
            feature_files = write_feature_files(
                features=package.bdd_features,
                output_directory=(
                    requirement_output_directory
                ),
            )

        # -----------------------------------------------------
        # Build requirement-level batch result
        # -----------------------------------------------------

        batch_status = map_quality_status(
            package.quality_gate.status
        )

        return BatchRequirementResult(
            requirement_id=(
                requirement.requirement_id
            ),
            title=requirement.title,
            status=batch_status,
            input_file=str(input_file),
            output_directory=str(
                requirement_output_directory
            ),
            json_output=str(
                json_output
            ),
            review_report=str(
                review_report
            ),
            traceability_matrix=str(
                traceability_matrix
            ),
            feature_files=[
                str(path)
                for path in feature_files
            ],
            requirement_coverage_percent=(
                package.coverage
                .requirement_coverage_percent
            ),
            acceptance_criteria_coverage_percent=(
                package.coverage
                .acceptance_criteria_coverage_percent
            ),
            acceptance_criteria_accountability_percent=(
                package.coverage
                .acceptance_criteria_accountability_percent
            ),
            acceptance_criteria_count=len(
                requirement.acceptance_criteria
            ),
            testable_ac_count=count_dispositions(
                package,
                VerificationDisposition.TESTABLE,
            ),
            limited_ac_count=count_dispositions(
                package,
                VerificationDisposition.LIMITED,
            ),
            blocked_ac_count=count_dispositions(
                package,
                VerificationDisposition.BLOCKED,
            ),
            finding_count=len(
                package.findings
            ),
            master_scenario_count=len(
                package.test_scenarios
            ),
            jama_test_case_count=len(
                package.jama_test_cases
            ),
            bdd_feature_count=len(
                package.bdd_features
            ),
            bdd_scenario_count=(
                count_bdd_scenarios(
                    package
                )
            ),
            jama_validation_status=(
                package.jama_validation.get(
                    "status"
                )
            ),
            bdd_validation_status=(
                package.bdd_validation.get(
                    "status"
                )
            ),
        )

    except json.JSONDecodeError as exc:
        return BatchRequirementResult(
            requirement_id=requirement_id,
            title=requirement_title,
            status=BatchItemStatus.ERROR,
            input_file=str(input_file),
            error_type="JSONDecodeError",
            error_message=str(exc),
        )

    except ValidationError as exc:
        return BatchRequirementResult(
            requirement_id=requirement_id,
            title=requirement_title,
            status=BatchItemStatus.ERROR,
            input_file=str(input_file),
            error_type="ValidationError",
            error_message=str(exc),
        )

    except Exception as exc:
        return BatchRequirementResult(
            requirement_id=requirement_id,
            title=requirement_title,
            status=BatchItemStatus.ERROR,
            input_file=str(input_file),
            error_type=type(exc).__name__,
            error_message=str(exc),
        )


def calculate_average(
    values: list[float],
) -> float:
    """
    Calculate a rounded arithmetic average.
    """

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        2,
    )


def build_batch_summary(
    run_id: str,
    results: list[BatchRequirementResult],
) -> BatchSummary:
    """
    Build deterministic aggregate batch statistics.
    """

    successful_results = [
        result
        for result in results
        if result.status
        != BatchItemStatus.ERROR
    ]

    return BatchSummary(
        run_id=run_id,

        total_requirements=len(
            results
        ),

        successfully_processed=len(
            successful_results
        ),

        processing_errors=sum(
            1
            for result in results
            if result.status
            == BatchItemStatus.ERROR
        ),

        pass_count=sum(
            1
            for result in results
            if result.status
            == BatchItemStatus.PASS
        ),

        review_count=sum(
            1
            for result in results
            if result.status
            == BatchItemStatus.REVIEW
        ),

        fail_count=sum(
            1
            for result in results
            if result.status
            == BatchItemStatus.FAIL
        ),

        total_acceptance_criteria=sum(
            result.acceptance_criteria_count
            for result in successful_results
        ),

        total_testable_acs=sum(
            result.testable_ac_count
            for result in successful_results
        ),

        total_limited_acs=sum(
            result.limited_ac_count
            for result in successful_results
        ),

        total_blocked_acs=sum(
            result.blocked_ac_count
            for result in successful_results
        ),

        total_findings=sum(
            result.finding_count
            for result in successful_results
        ),

        total_master_scenarios=sum(
            result.master_scenario_count
            for result in successful_results
        ),

        total_jama_test_cases=sum(
            result.jama_test_case_count
            for result in successful_results
        ),

        total_bdd_features=sum(
            result.bdd_feature_count
            for result in successful_results
        ),

        total_bdd_scenarios=sum(
            result.bdd_scenario_count
            for result in successful_results
        ),

        average_requirement_coverage_percent=(
            calculate_average(
                [
                    result.requirement_coverage_percent
                    for result
                    in successful_results
                ]
            )
        ),

        average_ac_coverage_percent=(
            calculate_average(
                [
                    result.acceptance_criteria_coverage_percent
                    for result
                    in successful_results
                ]
            )
        ),

        average_ac_accountability_percent=(
            calculate_average(
                [
                    result.acceptance_criteria_accountability_percent
                    for result
                    in successful_results
                ]
            )
        ),

        jama_validation_failures=sum(
            1
            for result in successful_results
            if result.jama_validation_status
            == "fail"
        ),

        bdd_validation_failures=sum(
            1
            for result in successful_results
            if result.bdd_validation_status
            == "fail"
        ),

        results=results,
    )


def write_batch_summary(
    summary: BatchSummary,
    run_output_directory: Path,
) -> Path:
    """
    Write batch-summary.json.
    """

    output_path = (
        run_output_directory
        / "batch-summary.json"
    )

    output_path.write_text(
        summary.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    return output_path


def run_batch(
    input_directory: Path,
    output_root: Path,
    project: str,
) -> tuple[BatchSummary, Path]:
    """
    Execute all discovered requirement files.

    One requirement failure does not terminate the batch.
    """

    requirement_files = (
        discover_requirement_files(
            input_directory
        )
    )

    run_id = create_run_id()

    run_output_directory = (
        output_root
        / "runs"
        / run_id
    )

    run_output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    for index, input_file in enumerate(
        requirement_files,
        start=1,
    ):
        print()
        print(
            f"[{index}/{len(requirement_files)}] "
            f"Processing {input_file.name}"
        )

        result = process_requirement_file(
            input_file=input_file,
            project=project,
            run_output_directory=(
                run_output_directory
            ),
        )

        results.append(
            result
        )

        print(
            "Result: "
            f"{result.status.value.upper()}"
        )

        if result.status == BatchItemStatus.ERROR:
            print(
                "Error: "
                f"{result.error_type}: "
                f"{result.error_message}"
            )

    summary = build_batch_summary(
        run_id=run_id,
        results=results,
    )

    summary_file = write_batch_summary(
        summary=summary,
        run_output_directory=(
            run_output_directory
        ),
    )

    return summary, summary_file