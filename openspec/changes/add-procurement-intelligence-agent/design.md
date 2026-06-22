## Context

FedEx procurement receives high request volume where many decisions are rule-driven. The current process relies on manual triage, creating delay and inconsistency for straightforward requests. This change introduces a single procurement intelligence workflow with strict decision precedence, structured outputs, and policy-aware rationale.

Key constraints:
- Runtime is Python 3.11+ with Pydantic v2 and pydantic-ai.
- The agent recommendation must always be one of approve, deny, or escalate and include a non-empty rationale.
- Tools and agent logic MUST load reference data through data/loader.py and MUST NOT read mock_data/ directly.
- The system must perform four checks for every request: budget, vendor duplication, policy compliance, and risk.

Stakeholders:
- Procurement officers (primary users of recommendations)
- Legal and Compliance (escalation consumers)
- Engineering and QA (implementation and test ownership)

## Goals / Non-Goals

**Goals:**
- Provide deterministic, explainable pre-screen recommendations for purchase requests.
- Enforce typed input/output contracts using Pydantic v2 models.
- Ensure all four checks execute per request and feed recommendation rationale.
- Implement precedence rules of escalate > deny > approve.
- Surface tool/data failures in rationale and route to safe escalation behavior.

**Non-Goals:**
- Fully automating final procurement approval (human remains final decision-maker).
- Replacing enterprise systems of record or external procurement platforms.
- Introducing new persistent storage beyond current mock-data-backed flow.
- Building UI workflows in this change.

## Decisions

### Decision 1: Use Pydantic AI with typed output contract
- Choice: Construct the main agent with output_type set to ProcurementRecommendation.
- Rationale: Enforces structured outputs and prevents free-form response drift.
- Alternative considered: Manual post-processing of string outputs.
- Why not alternative: Increases parsing fragility and weakens schema guarantees.

### Decision 2: Centralize data reads in data/loader.py
- Choice: Require all tools to retrieve budgets, vendors, policies, and requests via loader functions.
- Rationale: Produces a single integration seam for data sourcing, improves testability, and enforces project constraints.
- Alternative considered: Direct JSON reads inside each tool.
- Why not alternative: Duplicates I/O logic, increases inconsistency risk, and violates repository conventions.

### Decision 3: Keep four focused tools and aggregate in agent layer
- Choice: Implement check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk as separate tools with clear result payloads.
- Rationale: Improves tool selection clarity, test isolation, and traceable rationale composition.
- Alternative considered: Single monolithic evaluate_request tool.
- Why not alternative: Harder to test, less explainable, and reduces reuse.

### Decision 4: Enforce recommendation precedence escalate > deny > approve
- Choice: Resolve combined findings by priority where escalation conditions override denial, and denial overrides approval.
- Rationale: Prioritizes governance and safety in ambiguous or high-risk cases.
- Alternative considered: First-failure-wins rule.
- Why not alternative: Can mask higher-severity conditions and produce unsafe approvals.

### Decision 5: Treat tool failures as explicit escalation signals
- Choice: If any tool fails or returns error context, recommendation path escalates with rationale that names the failure.
- Rationale: Avoids silent partial decisions and preserves auditability.
- Alternative considered: Ignore failed checks and proceed with remaining signals.
- Why not alternative: Creates false confidence and potentially unsafe outcomes.

## Risks / Trade-offs

- [Risk] Policy text and sample labels include edge ambiguity (for example near-threshold escalation patterns) -> Mitigation: codify precedence in specs and cover boundary behavior in tests.
- [Risk] Tight coupling to mock data conventions during early sessions -> Mitigation: isolate data access behind loader interfaces to simplify future backend swap.
- [Risk] Overly strict validation could reject legitimate real-world variants -> Mitigation: define explicit validators and include targeted negative tests before widening rules.
- [Risk] Tool result schema drift can break rationale composition -> Mitigation: document tool output contracts in specs and test expected keys.

## Migration Plan

1. Add or align Pydantic models for request and recommendation contracts.
2. Ensure loader exposes required dataset access functions used by tools.
3. Implement/align four tools to return deterministic structured results.
4. Wire agent orchestration to call all four tools and apply precedence logic.
5. Add tool-level and agent-level tests covering approve, deny, escalate, and error handling.
6. Run openspec validation and full test suite before review.

Rollback strategy:
- Revert to last stable commit if recommendation logic regresses or tests fail.
- Because this is advisory logic, backout risk is low when controlled by test gating.

## Open Questions

- Should near-threshold escalation use a fixed percentage (for example 5%) or an explicit amount band?
- Should manager-threshold non-compliance (POL-002) force escalate or remain a rationale-only process note?
- Should ambiguous no-violation cases default to approve or conservative escalate?
