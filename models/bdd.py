from pydantic import BaseModel, Field


class BDDScenario(BaseModel):
    scenario_id: str
    name: str

    tags: list[str] = Field(
        default_factory=list
    )

    given: list[str] = Field(
        default_factory=list
    )

    when: list[str] = Field(
        default_factory=list
    )

    then: list[str] = Field(
        default_factory=list
    )

    master_scenario_ids: list[str] = Field(
        default_factory=list
    )

    requirement_ids: list[str] = Field(
        default_factory=list
    )

    acceptance_criteria_ids: list[str] = Field(
        default_factory=list
    )


class BDDFeature(BaseModel):
    feature_id: str
    name: str
    description: str

    tags: list[str] = Field(
        default_factory=list
    )

    requirement_ids: list[str] = Field(
        default_factory=list
    )

    scenarios: list[BDDScenario] = Field(
        default_factory=list
    )


class BDDFeatureCollection(BaseModel):
    features: list[BDDFeature] = Field(
        default_factory=list
    )