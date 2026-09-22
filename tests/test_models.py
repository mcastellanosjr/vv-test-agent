from models.requirement import Requirement, AcceptanceCriterion


def test_requirement_creation():

    requirement = Requirement(
        requirement_id="GXY-TEST-001",
        title="Test Requirement",
        text="The system shall display the software version.",
        acceptance_criteria=[
            AcceptanceCriterion(
                id="AC-01",
                text="Software version is displayed."
            )
        ]
    )

    assert requirement.requirement_id == "GXY-TEST-001"
    assert len(requirement.acceptance_criteria) == 1
    assert requirement.acceptance_criteria[0].id == "AC-01"