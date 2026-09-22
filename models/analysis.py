from pydantic import BaseModel, Field


class RequirementAnalysis(BaseModel):

    functional_area: str | None = None

    actors: list[str] = Field(default_factory=list)

    roles: list[str] = Field(default_factory=list)

    devices: list[str] = Field(default_factory=list)

    preconditions: list[str] = Field(default_factory=list)

    behaviors: list[str] = Field(default_factory=list)

    business_rules: list[str] = Field(default_factory=list)

    data_constraints: list[str] = Field(default_factory=list)

    states: list[str] = Field(default_factory=list)

    state_transitions: list[str] = Field(default_factory=list)

    error_conditions: list[str] = Field(default_factory=list)

    dependencies: list[str] = Field(default_factory=list)