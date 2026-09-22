from enum import Enum

from pydantic import BaseModel, Field


class TestType(str, Enum):
    HAPPY_PATH = "happy_path"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    ERROR_HANDLING = "error_handling"
    STATE_TRANSITION = "state_transition"
    PERMISSION = "permission"
    RECOVERY = "recovery"
    UI = "ui"
    INTEGRATION = "integration"


class TestScenario(BaseModel):

    scenario_id: str

    title: str

    objective: str

    test_type: TestType

    preconditions: list[str] = Field(default_factory=list)

    actions: list[str] = Field(default_factory=list)

    expected_behavior: list[str] = Field(default_factory=list)

    requirement_ids: list[str] = Field(default_factory=list)

    acceptance_criteria_ids: list[str] = Field(default_factory=list)

    risk_notes: list[str] = Field(default_factory=list)

    source: str = "generated"

class ScenarioCollection(BaseModel):
    scenarios: list[TestScenario] = Field(default_factory=list)