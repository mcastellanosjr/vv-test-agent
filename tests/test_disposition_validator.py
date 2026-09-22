from agent.disposition_validator import (
    validate_dispositions,
)
from models.disposition import (
    AcceptanceCriterionDisposition,
    DispositionCollection,
    VerificationDisposition,
)
from models.finding import FindingCollection
from models.requirement import (
    AcceptanceCriterion,
    Requirement,
)


def build_requirement():
    return Requirement(
        requirement_id="REQ-001",
        text="Test requirement.",
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-01",
                text="First criterion.",
            ),
            AcceptanceCriterion(
                id="AC-02",
                text="Second criterion.",
            ),
        ],
    )


def build_disposition(ac_id):
    return AcceptanceCriterionDisposition(
        acceptance_criterion_id=ac_id,
        disposition=VerificationDisposition.TESTABLE,
        rationale="Sufficient behavior is defined.",
        supported_behavior=[
            "Supported behavior."
        ],
    )


def test_complete_dispositions_pass():
    requirement = build_requirement()

    dispositions = DispositionCollection(
        dispositions=[
            build_disposition("AC-01"),
            build_disposition("AC-02"),
        ]
    )

    findings = FindingCollection(
        findings=[]
    )

    result = validate_dispositions(
        requirement=requirement,
        dispositions=dispositions,
        findings=findings,
    )

    assert result["valid"] is True
    assert result["errors"] == []


def test_missing_disposition_fails():
    requirement = build_requirement()

    dispositions = DispositionCollection(
        dispositions=[
            build_disposition("AC-01"),
        ]
    )

    findings = FindingCollection(
        findings=[]
    )

    result = validate_dispositions(
        requirement=requirement,
        dispositions=dispositions,
        findings=findings,
    )

    assert result["valid"] is False

    assert "AC-02" in (
        result["missing_ac_ids"]
    )


def test_duplicate_disposition_fails():
    requirement = build_requirement()

    dispositions = DispositionCollection(
        dispositions=[
            build_disposition("AC-01"),
            build_disposition("AC-01"),
            build_disposition("AC-02"),
        ]
    )

    findings = FindingCollection(
        findings=[]
    )

    result = validate_dispositions(
        requirement=requirement,
        dispositions=dispositions,
        findings=findings,
    )

    assert result["valid"] is False

    assert "AC-01" in (
        result["duplicate_ac_ids"]
    )


def test_unknown_ac_disposition_fails():
    requirement = build_requirement()

    dispositions = DispositionCollection(
        dispositions=[
            build_disposition("AC-01"),
            build_disposition("AC-02"),
            build_disposition("AC-999"),
        ]
    )

    findings = FindingCollection(
        findings=[]
    )

    result = validate_dispositions(
        requirement=requirement,
        dispositions=dispositions,
        findings=findings,
    )

    assert result["valid"] is False

    assert "AC-999" in (
        result["unknown_ac_ids"]
    )