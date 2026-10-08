from models.scenario_package import (
    VVScenarioDesignPackageV1,
)


def test_scenario_package_inherits_base_package():
    assert issubclass(
        VVScenarioDesignPackageV1,
        __import__(
            "models.package",
            fromlist=["VVDesignPackageV1"],
        ).VVDesignPackageV1,
    )


def test_scenario_package_contains_evidence_fields():
    fields = VVScenarioDesignPackageV1.model_fields

    assert "supplied_scenarios" in fields
    assert "source_validation" in fields
    assert "normalization" in fields
    assert "normalization_validation" in fields


def test_scenario_package_defaults_to_scenario_driven():
    field = VVScenarioDesignPackageV1.model_fields[
        "pipeline_mode"
    ]

    assert field.default == "scenario_driven"


def test_normalization_evidence_is_optional():
    fields = VVScenarioDesignPackageV1.model_fields

    assert fields["normalization"].default is None

    assert (
        fields["normalization_validation"].default
        is None
    )