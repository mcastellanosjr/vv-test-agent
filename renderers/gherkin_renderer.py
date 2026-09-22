import re
from pathlib import Path

from models.bdd import BDDFeature


def normalize_tag(tag: str) -> str:
    """
    Convert a structured tag into a Gherkin-compatible tag.

    Examples:

    GALAXY1-REQ-001
        -> @GALAXY1-REQ-001

    session timeout
        -> @session_timeout
    """

    normalized = tag.strip()

    if normalized.startswith("@"):
        normalized = normalized[1:]

    normalized = re.sub(
        r"\s+",
        "_",
        normalized,
    )

    normalized = re.sub(
        r"[^A-Za-z0-9_\-]",
        "_",
        normalized,
    )

    return f"@{normalized}"


def render_tags(tags: list[str]) -> str:
    """
    Render a list of tags as one Gherkin tag line.
    """

    unique_tags = []

    for tag in tags:
        rendered = normalize_tag(tag)

        if rendered not in unique_tags:
            unique_tags.append(rendered)

    return " ".join(unique_tags)


def render_feature(
    feature: BDDFeature,
) -> str:
    """
    Render one structured BDD feature into valid
    human-readable Gherkin syntax.
    """

    lines = []

    if feature.tags:
        lines.append(
            render_tags(feature.tags)
        )

    lines.append(
        f"Feature: {feature.name}"
    )

    if feature.description:
        lines.append("")

        for description_line in (
            feature.description.splitlines()
        ):
            lines.append(
                f"  {description_line.strip()}"
            )

    for scenario in feature.scenarios:
        lines.append("")

        if scenario.tags:
            lines.append(
                f"  {render_tags(scenario.tags)}"
            )

        lines.append(
            f"  Scenario: {scenario.name}"
        )

        # GIVEN
        for index, statement in enumerate(
            scenario.given
        ):
            keyword = (
                "Given"
                if index == 0
                else "And"
            )

            lines.append(
                f"    {keyword} {statement}"
            )

        # WHEN
        for index, statement in enumerate(
            scenario.when
        ):
            keyword = (
                "When"
                if index == 0
                else "And"
            )

            lines.append(
                f"    {keyword} {statement}"
            )

        # THEN
        for index, statement in enumerate(
            scenario.then
        ):
            keyword = (
                "Then"
                if index == 0
                else "And"
            )

            lines.append(
                f"    {keyword} {statement}"
            )

    lines.append("")

    return "\n".join(lines)


def create_feature_filename(
    feature: BDDFeature,
) -> str:
    """
    Create a deterministic filesystem-safe filename.
    """

    name = feature.name.lower()

    name = re.sub(
        r"[^a-z0-9]+",
        "_",
        name,
    )

    name = name.strip("_")

    return (
        f"{feature.feature_id.lower()}_"
        f"{name}.feature"
    )


def write_feature_files(
    features: list[BDDFeature],
    output_directory: Path,
) -> list[Path]:
    """
    Render and write all BDD features.

    Returns the paths of the generated feature files.
    """

    feature_directory = (
        output_directory / "features"
    )

    feature_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_files = []

    for feature in features:
        filename = create_feature_filename(
            feature
        )

        output_path = (
            feature_directory / filename
        )

        content = render_feature(
            feature
        )

        output_path.write_text(
            content,
            encoding="utf-8",
        )

        generated_files.append(
            output_path
        )

    return generated_files