from pydantic import BaseModel, Field


class AcceptanceCriterion(BaseModel):
    id: str = Field(description="Unique acceptance criterion identifier")
    text: str = Field(description="Acceptance criterion text")


class Requirement(BaseModel):
    requirement_id: str
    title: str | None = None
    text: str

    acceptance_criteria: list[AcceptanceCriterion] = Field(
        default_factory=list
    )