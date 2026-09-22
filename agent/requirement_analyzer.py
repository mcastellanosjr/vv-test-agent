from models.analysis import RequirementAnalysis
from models.requirement import Requirement

from agent.cursor_client import run_cursor_structured


SYSTEM_PROMPT = """
You are a Senior Verification and Validation Engineer working
in an FDA-regulated medical device software environment.

Analyze the supplied software requirement and acceptance criteria
for verification purposes.

Extract only information explicitly stated or directly supported
by the source.

Identify:

- functional area
- actors
- user roles
- devices or systems
- preconditions
- required behaviors
- business rules
- data constraints
- states
- state transitions
- error conditions
- dependencies

Rules:

1. Do not invent requirements.
2. Do not silently resolve ambiguities.
3. Do not introduce expected behavior unsupported by the source.
4. Distinguish explicit information from missing information.
5. Use objective verification-oriented language.
6. Preserve terminology from the source where appropriate.
7. Do not generate test cases or test scenarios during this stage.
"""


def analyze_requirement(
    requirement: Requirement,
) -> RequirementAnalysis:
    """
    Analyze a requirement using Cursor CLI and return
    a validated RequirementAnalysis object.
    """

    prompt = f"""
{SYSTEM_PROMPT}

SOURCE REQUIREMENT

{requirement.model_dump_json(indent=2)}

Analyze the source requirement according to the instructions above.
"""

    return run_cursor_structured(
        prompt=prompt,
        response_model=RequirementAnalysis,
    )