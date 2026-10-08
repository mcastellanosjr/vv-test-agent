from pydantic import Field

from models.package import VVDesignPackageV1
from models.scenario_normalization import (
    ScenarioNormalizationResult,
)
from models.scenario_normalization_validation import (
    ScenarioNormalizationValidationResult,
)
from models.scenario_validation import (
    SuppliedScenarioValidationResult,
)
from models.supplied_scenario import (
    SuppliedScenarioCollection,
)


class VVScenarioDesignPackageV1(VVDesignPackageV1):
    """
    Scenario-driven V&V package.

    Preserves original supplied scenarios and the
    evidence of their validation and normalization.
    """

    pipeline_mode: str = "scenario_driven"

    supplied_scenarios: SuppliedScenarioCollection = Field(
        default_factory=SuppliedScenarioCollection
    )

    source_validation: SuppliedScenarioValidationResult

    normalization: ScenarioNormalizationResult | None = None

    normalization_validation: (
        ScenarioNormalizationValidationResult | None
    ) = None