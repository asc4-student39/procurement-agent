## ADDED Requirements

### Requirement: Agent input and output contracts
The system SHALL define agent behavior in agent.py such that it accepts a
PurchaseRequest input and returns a ProcurementRecommendation output, using the
types defined in models.py.

#### Scenario: Typed agent boundary is enforced
- **WHEN** a request is evaluated by agent.py
- **THEN** the input is treated as PurchaseRequest and the final output conforms
  to ProcurementRecommendation

### Requirement: Tool registration and execution coverage
The agent in agent.py MUST register and execute all four procurement checks for
every request: check_budget, check_vendor_duplication, check_policy_compliance,
and assess_risk.

#### Scenario: All four checks run for one request
- **WHEN** a valid PurchaseRequest is evaluated
- **THEN** the agent executes check_budget, check_vendor_duplication,
  check_policy_compliance, and assess_risk before selecting a final decision

### Requirement: Decision space and precedence
The agent MUST produce a decision value of only approve, deny, or escalate and
SHALL apply precedence in this order when multiple checks fire: escalate,
then deny, then approve.

#### Scenario: Escalation takes priority over denial
- **WHEN** at least one check indicates escalation and another indicates denial
- **THEN** the final ProcurementRecommendation decision is escalate

### Requirement: Rationale completeness
The agent MUST always provide a non-empty rationale and SHALL include
traceable evidence from check outputs, including policy IDs and numeric context
when available.

#### Scenario: Rationale references decision evidence
- **WHEN** the agent returns deny or escalate
- **THEN** the rationale includes the triggering check evidence such as policy
  IDs, threshold status, risk level, or budget overage details

### Requirement: Tool error safety behavior
If any tool call fails or returns an error field, the agent MUST treat the
evaluation as safety-incomplete, SHALL return decision escalate, and MUST
include failure context in rationale.

#### Scenario: Tool error forces escalation
- **WHEN** one or more tool results include an error
- **THEN** the final decision is escalate and rationale names the failed tool
  and error context

### Requirement: System prompt constraints
The system prompt used by agent.py SHALL explicitly constrain behavior to:
run all four tools per request, follow escalate > deny > approve precedence,
keep decisions within approve/deny/escalate, and always produce a non-empty,
evidence-based rationale.

#### Scenario: Prompt defines non-negotiable constraints
- **WHEN** the agent is constructed in agent.py
- **THEN** its system prompt includes tool execution coverage, precedence,
  decision constraints, and rationale requirements as mandatory rules