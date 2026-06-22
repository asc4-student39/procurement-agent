## Why

FedEx procurement analysts spend time on high-volume requests that can be pre-screened with clear policy and risk checks. This change introduces a reliable, explainable procurement intelligence agent now so analysts can focus on complex exceptions while maintaining consistent governance outcomes.

## What Changes

- Add a Pydantic AI procurement agent that accepts a purchase request and returns a structured recommendation with decision constrained to approve, deny, or escalate plus a non-empty rationale.
- Add and enforce Pydantic v2 domain models for PurchaseRequest input and ProcurementRecommendation output.
- Add data access through data/loader.py for all mock data reads; tool and agent logic must not read mock_data/ directly.
- Add four procurement checks in tools/: check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk.
- Define and implement decision precedence as escalate > deny > approve.
- Require tool failure handling to surface errors in the rationale and produce a safe recommendation path.
- Add tests for each tool success path and end-to-end agent outcomes across approve, deny, and escalate scenarios.

## Capabilities

### New Capabilities
- `procurement-models`: Typed Pydantic v2 models for purchase request inputs and structured recommendations with constrained decision values.
- `procurement-data-loader`: Centralized data loading interface that is the only allowed access path to mock procurement datasets.
- `procurement-check-tools`: Budget, vendor duplication, policy compliance, and risk assessment tool behaviors with deterministic outputs for agent reasoning.
- `procurement-intelligence-agent`: Agent orchestration that runs all four checks, applies decision precedence, and emits rationale-rich recommendations.

### Modified Capabilities
- None.

## Impact

- Affected code: models.py, data/loader.py, tools/*.py, agent.py, and tests/.
- Affected behavior: procurement pre-screening flow and recommendation quality for advisory decisions.
- Dependencies: pydantic-ai for agent runtime, Pydantic v2 for schema validation, pytest and pytest-asyncio for verification.
- Risk controls: improved explainability and safer failure behavior through explicit escalation on tool errors.
