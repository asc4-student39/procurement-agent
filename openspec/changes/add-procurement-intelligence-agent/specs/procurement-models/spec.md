## ADDED Requirements

### Requirement: Purchase request input model validation
The system MUST define a PurchaseRequest model using Pydantic v2 and SHALL validate required request fields for identity, vendor, category, quantity, and pricing data before any procurement checks execute.

#### Scenario: Valid purchase request accepted
- **WHEN** a request includes all required fields with valid data types and non-negative monetary values
- **THEN** the model validation succeeds and the request is eligible for tool evaluation

### Requirement: Structured recommendation output contract
The system MUST define a ProcurementRecommendation model using Pydantic v2 where decision SHALL be constrained to approve, deny, or escalate and rationale SHALL be a non-empty string.

#### Scenario: Invalid decision value rejected
- **WHEN** recommendation output contains a decision value outside approve, deny, or escalate
- **THEN** model validation fails and the invalid recommendation is not accepted

### Requirement: Recommendation rationale integrity
The system SHALL require rationale text in every recommendation and MUST reject empty or whitespace-only rationale values.

#### Scenario: Empty rationale blocked
- **WHEN** a recommendation is produced with an empty rationale
- **THEN** output validation fails and the recommendation is treated as invalid
