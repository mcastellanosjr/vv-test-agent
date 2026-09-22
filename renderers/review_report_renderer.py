from pathlib import Path

from models.package import VVDesignPackageV1


LINE = "=" * 72
SUBLINE = "-" * 72


def format_status(value) -> str:
    """
    Convert Enum/string/None status values into a
    consistent uppercase display value.
    """

    if value is None:
        return "UNKNOWN"

    if hasattr(value, "value"):
        value = value.value

    return str(value).upper()


def format_list(values: list[str]) -> str:
    """
    Format a list for compact report display.
    """

    if not values:
        return "None"

    return ", ".join(values)


def count_bdd_scenarios(
    package: VVDesignPackageV1,
) -> int:
    """
    Count all BDD scenarios across all generated features.
    """

    return sum(
        len(feature.scenarios)
        for feature in package.bdd_features
    )


def build_ac_disposition_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    Build AC ID -> disposition object mapping.
    """

    return {
        disposition.acceptance_criterion_id: disposition
        for disposition
        in package.verification_dispositions
    }


def build_scenario_map(
    package: VVDesignPackageV1,
) -> dict:
    """
    Build AC ID -> master scenario IDs mapping.
    """

    mapping = {
        ac.id: []
        for ac in package.requirement.acceptance_criteria
    }

    for scenario in package.test_scenarios:
        for ac_id in scenario.acceptance_criteria_ids:
            if ac_id in mapping:
                mapping[ac_id].append(
                    scenario.scenario_id
                )

    return mapping


def render_review_report(
    package: VVDesignPackageV1,
) -> str:
    """
    Render a deterministic human-readable V&V review report.

    No AI model is used.
    """

    lines = []

    quality_gate = package.quality_gate

    disposition_map = build_ac_disposition_map(
        package
    )

    scenario_map = build_scenario_map(
        package
    )

    # =========================================================
    # Header
    # =========================================================

    lines.append(LINE)
    lines.append("V&V TEST DESIGN REVIEW REPORT")
    lines.append(LINE)
    lines.append("")

    lines.append(
        f"Project:      {package.project}"
    )

    lines.append(
        "Requirement:  "
        f"{package.requirement.requirement_id}"
    )

    lines.append(
        "Title:        "
        f"{package.requirement.title or 'N/A'}"
    )

    lines.append("")

    # =========================================================
    # Overall status
    # =========================================================

    lines.append("OVERALL STATUS")
    lines.append(SUBLINE)

    lines.append(
        "Quality Gate:                 "
        f"{format_status(quality_gate.status)}"
    )

    lines.append(
        "Requirement Review Status:    "
        f"{format_status(package.review_status)}"
    )

    lines.append("")

    lines.append(
        "Requirement Coverage:         "
        f"{package.coverage.requirement_coverage_percent:.2f}%"
    )

    lines.append(
        "AC Executable Coverage:       "
        f"{package.coverage.acceptance_criteria_coverage_percent:.2f}%"
    )

    lines.append(
        "AC Accountability:            "
        f"{package.coverage.acceptance_criteria_accountability_percent:.2f}%"
    )

    lines.append("")

    lines.append(
        "JAMA Validation:              "
        f"{format_status(package.jama_validation.get('status'))}"
    )

    lines.append(
        "BDD Validation:               "
        f"{format_status(package.bdd_validation.get('status'))}"
    )

    lines.append("")

    # =========================================================
    # Quality gate reasons
    # =========================================================

    lines.append("QUALITY GATE ASSESSMENT")
    lines.append(SUBLINE)

    if quality_gate.blocking_reasons:
        lines.append("Blocking Reasons:")

        for reason in quality_gate.blocking_reasons:
            lines.append(
                f"  - {reason}"
            )
    else:
        lines.append(
            "Blocking Reasons: None"
        )

    lines.append("")

    if quality_gate.review_reasons:
        lines.append("Review Reasons:")

        for reason in quality_gate.review_reasons:
            lines.append(
                f"  - {reason}"
            )
    else:
        lines.append(
            "Review Reasons: None"
        )

    lines.append("")

    # =========================================================
    # Findings
    # =========================================================

    lines.append("VERIFICATION FINDINGS")
    lines.append(SUBLINE)

    if not package.findings:
        lines.append(
            "No verification findings were identified."
        )

    else:
        for finding in package.findings:

            lines.append(
                f"{finding.id} | "
                f"{format_status(finding.severity)} | "
                f"{format_status(finding.finding_type)}"
            )

            lines.append(
                f"Description: {finding.description}"
            )

            lines.append(
                f"Impact:      {finding.impact}"
            )

            if finding.source_reference:
                lines.append(
                    "Source:      "
                    f"{finding.source_reference}"
                )

            if finding.clarification_question:
                lines.append(
                    "Question:    "
                    f"{finding.clarification_question}"
                )

            lines.append("")

    # =========================================================
    # AC dispositions
    # =========================================================

    lines.append(
        "AC VERIFICATION DISPOSITIONS"
    )

    lines.append(SUBLINE)

    for ac in package.requirement.acceptance_criteria:

        disposition = disposition_map.get(
            ac.id
        )

        lines.append(
            f"{ac.id}: {ac.text}"
        )

        if disposition is None:
            lines.append(
                "  Disposition: MISSING"
            )

            lines.append(
                "  WARNING: No verification disposition "
                "was generated."
            )

            lines.append("")
            continue

        lines.append(
            "  Disposition: "
            f"{format_status(disposition.disposition)}"
        )

        lines.append(
            f"  Rationale:   {disposition.rationale}"
        )

        if disposition.supported_behavior:
            lines.append(
                "  Supported Behavior:"
            )

            for behavior in disposition.supported_behavior:
                lines.append(
                    f"    - {behavior}"
                )

        if disposition.limitations:
            lines.append(
                "  Limitations:"
            )

            for limitation in disposition.limitations:
                lines.append(
                    f"    - {limitation}"
                )

        lines.append(
            "  Related Findings: "
            f"{format_list(disposition.related_finding_ids)}"
        )

        lines.append(
            "  Master Scenarios: "
            f"{format_list(scenario_map.get(ac.id, []))}"
        )

        lines.append("")

    # =========================================================
    # Master test design
    # =========================================================

    lines.append("MASTER TEST DESIGN")
    lines.append(SUBLINE)

    lines.append(
        "Master Scenarios:             "
        f"{len(package.test_scenarios)}"
    )

    lines.append(
        "Uncovered ACs:                "
        f"{format_list(package.coverage.uncovered_acceptance_criteria_ids)}"
    )

    lines.append(
        "Unaccounted ACs:              "
        f"{format_list(package.coverage.unaccounted_acceptance_criteria_ids)}"
    )

    lines.append(
        "Blocked ACs:                  "
        f"{format_list(package.coverage.blocked_acceptance_criteria_ids)}"
    )

    lines.append("")

    if package.test_scenarios:
        lines.append("Master Scenario Summary:")

        for scenario in package.test_scenarios:
            lines.append(
                f"  {scenario.scenario_id} | "
                f"{format_status(scenario.test_type)} | "
                f"{scenario.title}"
            )

            lines.append(
                "    Requirements: "
                f"{format_list(scenario.requirement_ids)}"
            )

            lines.append(
                "    ACs: "
                f"{format_list(scenario.acceptance_criteria_ids)}"
            )

        lines.append("")

    # =========================================================
    # Generated artifacts
    # =========================================================

    lines.append("GENERATED ARTIFACTS")
    lines.append(SUBLINE)

    lines.append(
        "JAMA Test Cases:              "
        f"{len(package.jama_test_cases)}"
    )

    lines.append(
        "BDD Features:                 "
        f"{len(package.bdd_features)}"
    )

    lines.append(
        "BDD Scenarios:                "
        f"{count_bdd_scenarios(package)}"
    )

    lines.append("")

    # =========================================================
    # Traceability health
    # =========================================================

    lines.append("TRACEABILITY HEALTH")
    lines.append(SUBLINE)

    lines.append(
        "Orphan Master Scenarios:      "
        f"{format_list(package.coverage.orphan_scenario_ids)}"
    )

    lines.append(
        "Invalid Requirement Refs:     "
        f"{format_list(package.coverage.invalid_requirement_references)}"
    )

    lines.append(
        "Invalid AC Refs:              "
        f"{format_list(package.coverage.invalid_acceptance_criteria_references)}"
    )

    lines.append(
        "Duplicate Scenario IDs:       "
        f"{format_list(package.coverage.duplicate_scenario_ids)}"
    )

    lines.append("")

    # =========================================================
    # Human review decision
    # =========================================================

    lines.append("HUMAN REVIEW DECISION")
    lines.append(SUBLINE)

    quality_status = format_status(
        quality_gate.status
    )

    if quality_status == "PASS":
        lines.append(
            "STRUCTURALLY READY FOR HUMAN REVIEW"
        )

        lines.append("")

        lines.append(
            "The generated V&V package passed the "
            "configured structural, coverage, and "
            "traceability controls."
        )

    elif quality_status == "REVIEW":
        lines.append(
            "HUMAN V&V REVIEW REQUIRED"
        )

        lines.append("")

        lines.append(
            "The generated V&V artifacts passed the "
            "configured structural controls, but one or "
            "more verification findings or blocked "
            "verification objectives require human "
            "assessment."
        )

    else:
        lines.append(
            "PACKAGE NOT READY FOR REVIEW RELEASE"
        )

        lines.append("")

        lines.append(
            "One or more configured structural or "
            "traceability gates failed. Resolve the "
            "blocking conditions before treating the "
            "generated package as complete."
        )

    lines.append("")
    lines.append(LINE)

    return "\n".join(lines)


def write_review_report(
    package: VVDesignPackageV1,
    output_directory: Path,
) -> Path:
    """
    Write the V&V review report to disk.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"{package.requirement.requirement_id}"
        "-review.txt"
    )

    output_path = (
        output_directory / filename
    )

    content = render_review_report(
        package
    )

    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return output_path