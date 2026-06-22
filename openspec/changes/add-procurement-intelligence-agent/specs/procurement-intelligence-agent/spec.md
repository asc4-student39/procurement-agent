## ADDED Requirements

### Requirement: Agent shall run all four checks per request
The system MUST execute check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk for every evaluated purchase request and SHALL avoid short-circuiting any check.

#### Scenario: Full check set executed
- **WHEN** a purchase request is submitted to the agent
- **THEN** all four tool evaluations are completed before final recommendation selection

### Requirement: Recommendation precedence and allowed outcomes
The agent MUST produce only approve, deny, or escalate outcomes and SHALL apply precedence in this order: escalate, then deny, then approve.

#### Scenario: Escalation overrides denial trigger
- **WHEN** a request contains both a deny trigger and a higher-priority escalation trigger
- **THEN** the final recommendation is escalate

### Requirement: Tool error safety behavior
If any tool reports an error, the agent MUST treat the request as safety-incomplete, SHALL return escalate, and MUST include the tool failure context in rationale.

#### Scenario: Tool failure routed to escalate
- **WHEN** one check returns an error payload
- **THEN** the recommendation is escalate with rationale naming the failed check

### Requirement: Rationale completeness and traceability
Every recommendation rationale MUST be non-empty and SHALL reference the specific check or policy evidence that drove the decision, including relevant monetary context when applicable.

#### Scenario: Denial rationale cites evidence
- **WHEN** a request is denied due to policy violation or budget overage
- **THEN** rationale references the triggering policy/check and includes supporting amount context

### Requirement: End-to-end sample request coverage
The system SHALL process all provided sample requests without unhandled exceptions and MUST support reachable approve, deny, and escalate outcomes under sample data.

#### Scenario: Sample corpus executes successfully
- **WHEN** the 15 sample requests are evaluated end-to-end
- **THEN** processing completes without crashes and produces recommendations across all required decision types
