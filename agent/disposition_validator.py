from collections import Counter

from models.disposition import DispositionCollection
from models.finding import FindingCollection
from models.requirement import Requirement


def validate_dispositions(
    requirement: Requirement,
    dispositions: DispositionCollection,
    findings: FindingCollection,
) -> dict:
    """
    Deterministically validate acceptance criterion
    verification dispositions.

    No AI model is used.
    """

    valid_ac_ids = {
        ac.id
        for ac in requirement.acceptance_criteria
    }

    valid_finding_ids = {
        finding.id
        for finding in findings.findings
    }

    disposition_ac_ids = [
        disposition.acceptance_criterion_id
        for disposition in dispositions.dispositions
    ]

    disposition_counts = Counter(
        disposition_ac_ids
    )

    # ---------------------------------------------------------
    # AC completeness
    # ---------------------------------------------------------

    missing_ac_ids = sorted(
        valid_ac_ids
        - set(disposition_ac_ids)
    )

    unknown_ac_ids = sorted(
        set(disposition_ac_ids)
        - valid_ac_ids
    )

    duplicate_ac_ids = sorted(
        ac_id
        for ac_id, count
        in disposition_counts.items()
        if count > 1
    )

    # ---------------------------------------------------------
    # Finding reference validation
    # ---------------------------------------------------------

    invalid_finding_references = sorted(
        {
            finding_id
            for disposition
            in dispositions.dispositions
            for finding_id
            in disposition.related_finding_ids
            if finding_id not in valid_finding_ids
        }
    )

    # ---------------------------------------------------------
    # Content checks
    # ---------------------------------------------------------

    empty_rationale_ac_ids = sorted(
        disposition.acceptance_criterion_id
        for disposition in dispositions.dispositions
        if not disposition.rationale.strip()
    )

    empty_supported_behavior_ac_ids = sorted(
        disposition.acceptance_criterion_id
        for disposition in dispositions.dispositions
        if not disposition.supported_behavior
    )

    # ---------------------------------------------------------
    # Errors
    # ---------------------------------------------------------

    errors = []

    if missing_ac_ids:
        errors.append(
            "One or more acceptance criteria are missing "
            "verification dispositions."
        )

    if unknown_ac_ids:
        errors.append(
            "Verification dispositions contain unknown "
            "acceptance criterion IDs."
        )

    if duplicate_ac_ids:
        errors.append(
            "One or more acceptance criteria have multiple "
            "verification dispositions."
        )

    if invalid_finding_references:
        errors.append(
            "Verification dispositions contain invalid "
            "finding references."
        )

    if empty_rationale_ac_ids:
        errors.append(
            "One or more verification dispositions have "
            "no rationale."
        )

    if empty_supported_behavior_ac_ids:
        errors.append(
            "One or more verification dispositions have "
            "no supported behavior."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "missing_ac_ids": missing_ac_ids,
        "unknown_ac_ids": unknown_ac_ids,
        "duplicate_ac_ids": duplicate_ac_ids,
        "invalid_finding_references": (
            invalid_finding_references
        ),
        "empty_rationale_ac_ids": (
            empty_rationale_ac_ids
        ),
        "empty_supported_behavior_ac_ids": (
            empty_supported_behavior_ac_ids
        ),
        "disposition_count": len(
            dispositions.dispositions
        ),
        "acceptance_criterion_count": len(
            valid_ac_ids
        ),
    }