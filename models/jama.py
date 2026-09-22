from pydantic import BaseModel, Field


class JamaTestStep(BaseModel):
    step_number: int
    action: str
    expected_result: str


class JamaTestCase(BaseModel):
    test_case_id: str
    name: str
    purpose: str
    description: str
    preconditions: list[str] = Field(default_factory=list)
    steps: list[JamaTestStep] = Field(default_factory=list)

    scenario_ids: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    acceptance_criteria_ids: list[str] = Field(
        default_factory=list
    )


class JamaTestCaseCollection(BaseModel):
    test_cases: list[JamaTestCase] = Field(
        default_factory=list
    )