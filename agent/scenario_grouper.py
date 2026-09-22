from agent.cursor_client import run_cursor_structured

from models.finding import FindingCollection
from models.grouping import ScenarioGrouping
from models.requirement import Requirement
from models.scenario import ScenarioCollection


SYSTEM_PROMPT = """
You are a Senior Verification and Validation Engineer working
in an FDA-regulated medical device software environment.

Your task is to organize supplied MASTER TEST SCENARIOS into
logical verification groups.

These groups will be used to generate formal JAMA verification
test cases.

GROUPING PRINCIPLES

Group scenarios when they share one or more meaningful
verification characteristics such as:

- the same functional area
- the same workflow
- the same screen or component
- the same business or domain behavior
- the same system state or state transition
- the same device type or device family
- the same role or permission model
- substantially the same setup or preconditions
- the same verification objective
- a natural sequential workflow

Do NOT combine scenarios merely to reduce the number of
test cases.

Keep scenarios separate when combining them would make the
resulting test case:

- difficult to understand
- difficult to execute
- difficult to maintain
- difficult to troubleshoot
- overly broad
- dependent on unrelated setup
- dependent on unrelated workflows

TRACEABILITY RULES

1. Every supplied scenario must appear in exactly one group.

2. Do not invent scenario IDs.

3. Do not omit scenarios.

4. Do not duplicate scenarios across groups.

5. Preserve meaningful functional distinctions.

6. Grouping must not change the verification intent of any
   source scenario.

7. Findings may inform grouping but must not be silently resolved.

GROUP IDENTIFIERS

Use sequential identifiers:

GRP-001
GRP-002
GRP-003

and continue as necessary.

Return only the structured grouping requested by the schema.
"""


def group_scenarios(
    requirement: Requirement,
    scenarios: ScenarioCollection,
    findings: FindingCollection,
) -> ScenarioGrouping:
    """
    Logically group master scenarios for downstream
    JAMA test-case generation.
    """

    prompt = f"""
{SYSTEM_PROMPT}

SOURCE REQUIREMENT

{requirement.model_dump_json(indent=2)}

MASTER TEST SCENARIOS

{scenarios.model_dump_json(indent=2)}

VERIFICATION FINDINGS

{findings.model_dump_json(indent=2)}

Before returning the grouping, verify that:

1. Every source scenario appears exactly once.

2. No unknown scenario ID is present.

3. Related scenarios are grouped only when doing so creates a
   coherent executable verification objective.

4. Unrelated behaviors remain in separate groups.

5. The minimum number of coherent groups is used without
   sacrificing clarity or maintainability.
"""

    return run_cursor_structured(
        prompt=prompt,
        response_model=ScenarioGrouping,
    )