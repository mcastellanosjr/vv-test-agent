from agent.cursor_client import run_cursor_structured

from models.analysis import RequirementAnalysis
from models.disposition import DispositionCollection
from models.finding import FindingCollection
from models.requirement import Requirement


SYSTEM_PROMPT = """
You are a Senior Verification and Validation Engineer working
in an FDA-regulated medical device software environment.

Your task is to assign a VERIFICATION DISPOSITION to every
acceptance criterion in the supplied requirement.

This step occurs before master test scenario generation.

The purpose is to ensure that every acceptance criterion is
explicitly accounted for and that acceptance criteria do not
silently disappear from downstream verification artifacts.


AVAILABLE DISPOSITIONS

TESTABLE

Use TESTABLE when the acceptance criterion defines sufficient
behavior and observable expected results to support meaningful
verification without inventing behavior.


LIMITED

Use LIMITED when meaningful verification is possible, but one
or more ambiguities, omissions, or specification limitations
prevent complete or precise verification.

A LIMITED acceptance criterion should still identify the
behavior that can be verified from the source.

Do not classify an acceptance criterion as BLOCKED merely
because additional detail would improve test precision.


BLOCKED

Use BLOCKED only when no defensible executable verification
scenario can be created without inventing required behavior or
an expected result.

BLOCKED should be used sparingly.

A missing implementation detail alone does not necessarily make
an acceptance criterion BLOCKED if its externally observable
behavior can still be meaningfully verified.


IMPORTANT RULES

1. Evaluate every supplied acceptance criterion.

2. Return exactly one disposition for every acceptance
   criterion.

3. Do not invent acceptance criterion IDs.

4. Do not omit acceptance criteria.

5. Do not duplicate acceptance criteria.

6. Evaluate the parent requirement and acceptance criteria as
   one integrated specification.

7. Acceptance criteria may add detail to or qualify the parent
   requirement.

8. Use existing findings when they materially affect
   verification.

9. Do not manufacture new ambiguity merely to justify LIMITED
   or BLOCKED.

10. Do not silently resolve existing findings.

11. The supported_behavior field must contain only behavior
    directly supported by the requirement or acceptance
    criterion.

12. The limitations field should identify only limitations that
    materially affect verification.

13. related_finding_ids may contain only finding IDs supplied
    in the input.

14. Do not classify an acceptance criterion as TESTABLE simply
    to achieve complete coverage.

15. Do not classify an acceptance criterion as BLOCKED simply
    because the specification is not ideal.

16. The disposition must reflect what can defensibly be
    verified from the supplied specification.
"""


def analyze_dispositions(
    requirement: Requirement,
    analysis: RequirementAnalysis,
    findings: FindingCollection,
) -> DispositionCollection:
    """
    Determine verification disposition for every
    acceptance criterion.
    """

    prompt = f"""
{SYSTEM_PROMPT}

REQUIREMENT

{requirement.model_dump_json(indent=2)}

REQUIREMENT ANALYSIS

{analysis.model_dump_json(indent=2)}

VERIFICATION FINDINGS

{findings.model_dump_json(indent=2)}

Assign exactly one verification disposition to every supplied
acceptance criterion.

Before returning the result verify that:

1. Every acceptance criterion is represented exactly once.
2. No unknown acceptance criterion ID is present.
3. Every related finding ID exists in the supplied findings.
4. TESTABLE, LIMITED, and BLOCKED are used according to the
   definitions above.
5. No unsupported behavior has been introduced.
"""

    return run_cursor_structured(
        prompt=prompt,
        response_model=DispositionCollection,
    )