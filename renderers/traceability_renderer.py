import csv
from pathlib import Path

from models.package import VVDesignPackageV1


def enum_value(value) -> str:
    """
    Convert an Enum or other value to a plain string.
    """

    if value is None:
        return ""

    if hasattr(value, "value"):
        return str(value.value)

    return str(value)


def join_values(values: list[str]) -> str:
    """
    Join multiple traceability references into one
    readable CSV cell.
    """

    if not values:
        return ""

    return "; ".join(
        sorted(set(values))
    )


def build_disposition_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    AC ID -> verification disposition.
    """

    return {
        item.acceptance_criterion_id: item
        for item in package.verification_dispositions
    }


def build_master_scenario_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    AC ID -> master scenarios.
    """

    mapping = {
        ac.id: []
        for ac in package.requirement.acceptance_criteria
    }

    for scenario in package.test_scenarios:

        for ac_id in scenario.acceptance_criteria_ids:

            if ac_id in mapping:
                mapping[ac_id].append(
                    scenario
                )

    return mapping


def build_jama_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    Master scenario ID -> JAMA test cases.
    """

    mapping = {}

    for test_case in package.jama_test_cases:

        for scenario_id in test_case.scenario_ids:

            mapping.setdefault(
                scenario_id,
                [],
            ).append(
                test_case
            )

    return mapping


def build_bdd_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    Master scenario ID -> BDD scenarios and feature data.
    """

    mapping = {}

    for feature in package.bdd_features:

        for scenario in feature.scenarios:

            for master_scenario_id in (
                scenario.master_scenario_ids
            ):

                mapping.setdefault(
                    master_scenario_id,
                    [],
                ).append(
                    {
                        "feature_id": (
                            feature.feature_id
                        ),
                        "feature_name": (
                            feature.name
                        ),
                        "scenario": scenario,
                    }
                )

    return mapping


def build_finding_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    Finding ID -> finding object.
    """

    return {
        finding.id: finding
        for finding in package.findings
    }


def build_traceability_rows(
    package: VVDesignPackageV1,
) -> list[dict]:
    """
    Build deterministic traceability rows.

    One row is produced for each acceptance criterion /
    master scenario combination.

    If an AC has no executable master scenario, one row is
    still produced so BLOCKED or unaccounted verification
    objectives remain visible.
    """

    rows = []

    disposition_map = build_disposition_map(
        package
    )

    master_map = build_master_scenario_map(
        package
    )

    jama_map = build_jama_map(
        package
    )

    bdd_map = build_bdd_map(
        package
    )

    finding_map = build_finding_map(
        package
    )

    requirement = package.requirement

    for ac in requirement.acceptance_criteria:

        disposition = disposition_map.get(
            ac.id
        )

        master_scenarios = master_map.get(
            ac.id,
            [],
        )

        # -----------------------------------------------------
        # Preserve visibility even when no executable
        # master scenario exists.
        # -----------------------------------------------------

        if not master_scenarios:

            finding_ids = []

            if disposition is not None:
                finding_ids = (
                    disposition.related_finding_ids
                )

            findings = [
                finding_map[finding_id]
                for finding_id in finding_ids
                if finding_id in finding_map
            ]

            rows.append(
                {
                    "requirement_id": (
                        requirement.requirement_id
                    ),
                    "requirement_title": (
                        requirement.title or ""
                    ),
                    "acceptance_criterion_id": (
                        ac.id
                    ),
                    "acceptance_criterion": (
                        ac.text
                    ),
                    "disposition": (
                        enum_value(
                            disposition.disposition
                        )
                        if disposition
                        else ""
                    ),
                    "disposition_rationale": (
                        disposition.rationale
                        if disposition
                        else ""
                    ),
                    "finding_ids": (
                        join_values(
                            [
                                finding.id
                                for finding
                                in findings
                            ]
                        )
                    ),
                    "finding_severities": (
                        join_values(
                            [
                                enum_value(
                                    finding.severity
                                )
                                for finding
                                in findings
                            ]
                        )
                    ),
                    "master_scenario_id": "",
                    "master_scenario_title": "",
                    "master_test_type": "",
                    "jama_test_case_ids": "",
                    "jama_test_case_names": "",
                    "bdd_feature_ids": "",
                    "bdd_feature_names": "",
                    "bdd_scenario_ids": "",
                    "bdd_scenario_names": "",
                    "executable_coverage": "No",
                    "accounted_for": (
                        "Yes"
                        if disposition
                        else "No"
                    ),
                }
            )

            continue

        # -----------------------------------------------------
        # AC has executable master scenario coverage
        # -----------------------------------------------------

        for master_scenario in master_scenarios:

            jama_cases = jama_map.get(
                master_scenario.scenario_id,
                [],
            )

            bdd_entries = bdd_map.get(
                master_scenario.scenario_id,
                [],
            )

            finding_ids = []

            if disposition is not None:
                finding_ids.extend(
                    disposition.related_finding_ids
                )

            findings = [
                finding_map[finding_id]
                for finding_id in finding_ids
                if finding_id in finding_map
            ]

            rows.append(
                {
                    "requirement_id": (
                        requirement.requirement_id
                    ),
                    "requirement_title": (
                        requirement.title or ""
                    ),
                    "acceptance_criterion_id": (
                        ac.id
                    ),
                    "acceptance_criterion": (
                        ac.text
                    ),
                    "disposition": (
                        enum_value(
                            disposition.disposition
                        )
                        if disposition
                        else ""
                    ),
                    "disposition_rationale": (
                        disposition.rationale
                        if disposition
                        else ""
                    ),
                    "finding_ids": (
                        join_values(
                            [
                                finding.id
                                for finding
                                in findings
                            ]
                        )
                    ),
                    "finding_severities": (
                        join_values(
                            [
                                enum_value(
                                    finding.severity
                                )
                                for finding
                                in findings
                            ]
                        )
                    ),
                    "master_scenario_id": (
                        master_scenario.scenario_id
                    ),
                    "master_scenario_title": (
                        master_scenario.title
                    ),
                    "master_test_type": (
                        enum_value(
                            master_scenario.test_type
                        )
                    ),
                    "jama_test_case_ids": (
                        join_values(
                            [
                                test_case.test_case_id
                                for test_case
                                in jama_cases
                            ]
                        )
                    ),
                    "jama_test_case_names": (
                        join_values(
                            [
                                test_case.name
                                for test_case
                                in jama_cases
                            ]
                        )
                    ),
                    "bdd_feature_ids": (
                        join_values(
                            [
                                entry["feature_id"]
                                for entry
                                in bdd_entries
                            ]
                        )
                    ),
                    "bdd_feature_names": (
                        join_values(
                            [
                                entry["feature_name"]
                                for entry
                                in bdd_entries
                            ]
                        )
                    ),
                    "bdd_scenario_ids": (
                        join_values(
                            [
                                entry["scenario"].scenario_id
                                for entry
                                in bdd_entries
                            ]
                        )
                    ),
                    "bdd_scenario_names": (
                        join_values(
                            [
                                entry["scenario"].name
                                for entry
                                in bdd_entries
                            ]
                        )
                    ),
                    "executable_coverage": "Yes",
                    "accounted_for": (
                        "Yes"
                        if disposition
                        else "No"
                    ),
                }
            )

    return rows


def write_traceability_matrix(
    package: VVDesignPackageV1,
    output_directory: Path,
) -> Path:
    """
    Write deterministic V&V traceability matrix as CSV.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / (
            f"{package.requirement.requirement_id}"
            "-traceability.csv"
        )
    )

    rows = build_traceability_rows(
        package
    )

    fieldnames = [
        "requirement_id",
        "requirement_title",
        "acceptance_criterion_id",
        "acceptance_criterion",
        "disposition",
        "disposition_rationale",
        "finding_ids",
        "finding_severities",
        "master_scenario_id",
        "master_scenario_title",
        "master_test_type",
        "jama_test_case_ids",
        "jama_test_case_names",
        "bdd_feature_ids",
        "bdd_feature_names",
        "bdd_scenario_ids",
        "bdd_scenario_names",
        "executable_coverage",
        "accounted_for",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    return output_path