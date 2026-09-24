import json

from agent.cursor_client import (
    run_cursor_structured,
)
from models.analysis import (
    RequirementAnalysis,
)
from models.finding import (
    FindingCollection,
)
from models.requirement import (
    Requirement,
)
from models.scenario_normalization import (
    ScenarioNormalizationResult,
)
from models.supplied_scenario import (
    SuppliedScenarioCollection,
)


def normalize_supplied_scenarios(
    requirement: Requirement,
    analysis: RequirementAnalysis,
    findings: FindingCollection,
    supplied_scenarios: (
        SuppliedScenarioCollection
    ),
) -> ScenarioNormalizationResult:
    """
    Normalize human-supplied test scenarios into the
    canonical TestScenario model.

    Cursor performs semantic interpretation only.
    Deterministic validation must be performed separately
    after this function returns.
    """

    prompt = f"""
You are a Senior Verification & Validation Engineer working
in an FDA-regulated medical device software environment.

Your task is to normalize HUMAN-SUPPLIED TEST SCENARIOS into
the canonical master test scenario structure.

The supplied scenarios are SOURCE EVIDENCE.

You must preserve their verification intent.

You are NOT being asked to redesign the test strategy.

============================================================
REQUIREMENT
============================================================

{json.dumps(
    requirement.model_dump(mode="json"),
    indent=2,
)}

============================================================
REQUIREMENT ANALYSIS
============================================================

{json.dumps(
    analysis.model_dump(mode="json"),
    indent=2,
)}

============================================================
VERIFICATION FINDINGS
============================================================

{json.dumps(
    findings.model_dump(mode="json"),
    indent=2,
)}

============================================================
SUPPLIED TEST SCENARIOS
============================================================

{json.dumps(
    supplied_scenarios.model_dump(
        mode="json"
    ),
    indent=2,
)}

============================================================
NORMALIZATION RULES
============================================================

1. The supplied scenarios are the primary source for this
   task.

2. Do NOT silently replace a supplied scenario with a newly
   invented scenario.

3. Do NOT invent:
   - system behavior
   - expected results
   - UI labels
   - controls
   - messages
   - timing tolerances
   - navigation
   - roles
   - devices
   - states
   - state transitions
   - recovery behavior
   - error handling

4. You may normalize wording and structure when doing so
   does not change the verification meaning.

5. Every supplied scenario must receive exactly one
   normalization record.

6. A supplied scenario may have one of these statuses:

   ACCEPTED
   The supplied scenario contains sufficient supported
   verification behavior and can be represented as one or
   more canonical master scenarios.

   LIMITED
   The supplied scenario contains meaningful supported
   verification behavior, but ambiguity, incompleteness or
   a source limitation prevents full precision.

   REJECTED
   The supplied scenario cannot be defensibly represented
   as an executable master scenario without inventing
   behavior, or it is outside the supplied requirement
   scope.

7. ACCEPTED and LIMITED scenarios must map to at least one
   normalized master scenario.

8. REJECTED scenarios must not map to any normalized master
   scenario.

9. LIMITED scenarios must preserve the relevant limitation
   in:
   - the normalization record limitations field, and
   - the normalized TestScenario risk_notes when applicable.

10. Do not use LIMITED merely because wording could be
    improved. Use it only when a meaningful verification
    limitation exists.

11. Do not use REJECTED merely because a scenario is
    imperfect. Use it only when executable normalization
    would require unsupported invention or when the
    scenario is outside requirement scope.

12. Normalized master scenario IDs must be sequential:

    TS-001
    TS-002
    TS-003
    ...

13. The normalized TestScenario source field must be:

    supplied

14. Every normalized scenario must trace to the supplied
    requirement:

    {requirement.requirement_id}

15. Acceptance criterion mappings may contain only AC IDs
    that exist in the supplied requirement.

16. Preserve supplied AC mappings when they are supported
    by the scenario behavior.

17. If a supplied scenario has no AC mapping, you may map it
    to an AC only when the relationship is directly
    supported by the observable scenario behavior and the
    supplied requirement.

18. Do not create additional scenarios merely to improve
    requirement coverage.

19. Do not create negative, boundary, recovery, permission
    or error scenarios unless that behavior already exists
    in the supplied scenario.

20. One supplied scenario may normalize into more than one
    master scenario only when the supplied scenario itself
    clearly contains multiple distinct executable
    verification behaviors.

21. Multiple supplied scenarios may map to one normalized
    scenario only when they genuinely represent the same
    verification behavior. Do not merge merely to reduce
    scenario count.

22. The normalized expected_behavior must contain only
    observable results supported by the supplied scenario
    and requirement.

23. Findings may inform limitations, but findings must not
    be silently resolved.

24. Do not infer missing behavior from common product
    conventions or testing best practices.

============================================================
FINAL SELF-CHECK
============================================================

Before returning the result verify:

- Every supplied source scenario ID has exactly one record.
- ACCEPTED and LIMITED records have normalized mappings.
- REJECTED records have no normalized mappings.
- Every mapped normalized ID exists.
- Every normalized scenario is mapped from at least one
  supplied scenario.
- All requirement references are in scope.
- All AC references are in scope.
- All normalized scenario IDs are unique.
- All normalized scenario source fields equal "supplied".
- No unsupported behavior was introduced.
"""

    return run_cursor_structured(
        prompt=prompt,
        response_model=(
            ScenarioNormalizationResult
        ),
    )