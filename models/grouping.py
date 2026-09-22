from pydantic import BaseModel, Field


class ScenarioGroup(BaseModel):
    group_id: str
    name: str
    rationale: str
    scenario_ids: list[str] = Field(default_factory=list)


class ScenarioGrouping(BaseModel):
    groups: list[ScenarioGroup] = Field(default_factory=list)