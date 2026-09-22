from agent.cursor_client import run_cursor_structured

from models.finding import FindingCollection
from models.grouping import ScenarioGrouping
from models.jama import JamaTestCaseCollection
from models.requirement import Requirement
from models.scenario import ScenarioCollection


SYSTEM_PROMPT = """
You are a Senior Verification and Validation Engineer working
in an FDA-regulated medical device software environment.

Generate formal, audit-ready JAMA verification test cases from
the supplied MASTER TEST SCENARIOS and approved logical scenario
grouping.

The master scenarios are the verification source of truth.

Do not expand the verification scope beyond the source
requirement, acceptance criteria, and master scenarios.


JAMA TEST CASE REQUIREMENTS

Each test case shall contain:

- test case ID
- name
- purpose
- description
- preconditions
- sequential test steps
- expected result for every test step
- source scenario IDs
- requirement IDs
- acceptance criterion IDs


TEST DESIGN RULES

1. Generate one JAMA test case for each supplied logical group.

2. Preserve the verification intent of every master scenario.

3. A grouped test case may verify multiple related scenarios
   when they form a coherent workflow.

4. Do not create one test case per scenario unless the grouping
   requires it.

5. Do not invent system behavior.

6. Do not invent UI controls, labels, messages, navigation,
   timing tolerances, roles, devices, states, or recovery
   behavior not supported by the source.

7. Do not silently resolve findings.

8. If a finding affects execution precision, preserve the
   supported verification objective without inventing the
   missing information.

9. Use objective, regulatory-friendly language.

10. Actions shall describe what the tester does.

11. Expected results shall describe observable system behavior.

12. Do not combine an action and expected result into the same
    statement.

13. Keep steps executable and logically ordered.

14. Avoid unnecessary implementation details.

15. Avoid subjective terms such as:
    - correctly
    - properly
    - appropriately
    - as expected
    unless the exact observable result is also stated.


TRACEABILITY RULES

16. Every generated test case must reference all master scenarios
    represented by its logical group.

17. Requirement IDs must come only from the supplied source.

18. Acceptance criterion IDs must come only from the supplied
    source.

19. Acceptance criteria shall be mapped only when actually
    verified by the test case.

20. Do not create orphan test cases.


TEST CASE IDENTIFIERS

Use sequential identifiers:

TC-001
TC-002
TC-003

and continue as required.
"""


def generate_jama_test_cases(
    requirement: Requirement,
    scenarios: ScenarioCollection,
    grouping: ScenarioGrouping,
    findings: FindingCollection,
) -> JamaTestCaseCollection:
    """
    Generate formal JAMA test cases from the master
    scenarios and logical grouping.
    """

    prompt = f"""
{SYSTEM_PROMPT}

SOURCE REQUIREMENT

{requirement.model_dump_json(indent=2)}

MASTER TEST SCENARIOS

{scenarios.model_dump_json(indent=2)}

LOGICAL SCENARIO GROUPING

{grouping.model_dump_json(indent=2)}

VERIFICATION FINDINGS

{findings.model_dump_json(indent=2)}

Before returning the test cases, verify that:

1. Every logical group has exactly one JAMA test case.

2. Every grouped source scenario is represented.

3. No unknown scenario ID is referenced.

4. Requirement and acceptance criterion mappings are valid.

5. No unsupported expected behavior has been introduced.

6. Every test step contains both an action and an objectively
   observable expected result.

7. Test case IDs are sequential and unique.
"""

    return run_cursor_structured(
        prompt=prompt,
        response_model=JamaTestCaseCollection,
    )