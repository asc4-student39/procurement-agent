## ADDED Requirements

### Requirement: Budget check behavior
The system MUST provide a check_budget tool that evaluates request total against cost center remaining budget and SHALL indicate whether the request is within budget and any overage amount.

#### Scenario: Overage detected
- **WHEN** request total exceeds remaining budget for the referenced cost center
- **THEN** check_budget reports within_budget as false and includes overage details

### Requirement: Vendor duplication and single-source behavior
The system MUST provide a check_vendor_duplication tool that detects contracted-vendor conflicts for covered categories and SHALL flag single-source violations when threshold conditions apply.

#### Scenario: Single-source violation returned
- **WHEN** a request above policy threshold uses a non-contracted vendor in a category with active contracted alternatives
- **THEN** check_vendor_duplication reports a policy violation with contracted-vendor context

### Requirement: Policy compliance evaluation
The system MUST provide a check_policy_compliance tool that evaluates applicable policy rules by category, amount, quantity, and vendor contract state, and SHALL return violation details with forced decision signals where policy requires deny or escalate.

#### Scenario: Catering prohibition enforced
- **WHEN** request category is catering
- **THEN** check_policy_compliance returns a violation indicating denial is required

### Requirement: Risk assessment evaluation
The system MUST provide an assess_risk tool that classifies vendor-related risk using contract status and compliance flags, and SHALL identify critical risk requiring escalation.

#### Scenario: Compliance-flagged vendor escalated
- **WHEN** vendor data indicates an active compliance flag
- **THEN** assess_risk returns critical risk classification and escalation guidance

### Requirement: Tool output stability for rationale composition
Each procurement tool MUST return deterministic, structured payloads with keys required by agent rationale composition, including explicit error fields when evaluation cannot complete.

#### Scenario: Tool failure includes error key
- **WHEN** a tool encounters a loader or evaluation failure
- **THEN** the tool response includes an error field that can be surfaced in recommendation rationale
