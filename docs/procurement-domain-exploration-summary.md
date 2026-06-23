# Procurement Domain Exploration Summary

## Scope

This summary analyzes domain behavior from the following data sources:

- mock_data/requests.json
- mock_data/policies.json
- mock_data/vendors.json
- mock_data/budgets.json

The objective is to document request fields, required checks, decision mapping rules,
and edge cases visible in sample data.

## 1) Purchase Request Fields

Each purchase request record contains the following fields.

| Field | Type | Meaning |
|---|---|---|
| request_id | string | Unique request identifier (REQ-###). |
| requestor | string | Person submitting the request. |
| cost_center_id | string | Cost center key used for budget lookup. |
| vendor_name | string | Human-readable vendor name. |
| vendor_id | string | Vendor key used for vendor lookup. |
| category | string | Procurement category used in policy checks. |
| item_description | string | Description of requested goods/services. |
| quantity | number | Requested units or hours depending on category. |
| unit_price | number | Price per unit in USD. |
| total_amount | number | Total request amount in USD. |
| expected_outcome | string | Sample oracle label (approve, deny, escalate, ambiguous). |
| outcome_reason | string | Sample oracle rationale text. |

Note: expected_outcome and outcome_reason are dataset labels for validation and
behavior analysis.

## 2) Four Checks The Agent Must Perform

The procurement domain implies four mandatory checks.

| Check | Primary Inputs | What It Verifies |
|---|---|---|
| Budget check | request.cost_center_id, request.total_amount, budgets.remaining | Request does not exceed remaining cost center budget (POL-008 baseline). |
| Vendor duplication check | request.vendor_id, request.category, request.total_amount, vendor contracts | For covered categories above 25,000 USD, request uses contracted vendor if active alternatives exist (POL-001). |
| Policy compliance check | request category/amount/quantity, vendor contract state | Applies explicit policy constraints: POL-002 to POL-008, including prohibited category and staffing constraints. |
| Risk assessment check | vendor.compliance_flag, vendor.contract_status, amount context | Escalation/denial risk based on compliance hold, contract health, and governance thresholds. |

## 3) Decision Mapping Rules

Observed mapping from policy definitions and sample outcomes:

### Decision Priority Matrix

| Condition | Default Action | Policy / Data Basis |
|---|---|---|
| Vendor is compliance-flagged | escalate | POL-006; REQ-011 |
| Amount at or above 50,000 USD | escalate | POL-003 |
| Near director threshold governance risk | escalate | REQ-014 pattern (within 5 percent of 50,000) |
| Prohibited category catering | deny | POL-004; REQ-009 |
| Vendor contract expired | deny | POL-005; REQ-007 |
| Single-source violation over 25,000 | deny | POL-001; REQ-008 |
| Budget overage | deny (baseline) | POL-008; REQ-006 |
| None of the above | approve | REQ-001 to REQ-005, REQ-012, REQ-013 |

### Conflict Resolution

When multiple signals are present, data suggests this precedence model:

1. Escalate for explicit governance/legal risk signals.
2. Deny for hard policy prohibitions and contract violations.
3. Approve only when no escalation or denial signals apply.

Important sample exception:

- REQ-010 exceeds budget but is labeled escalate due to near-director-threshold
  governance context. This indicates a deliberate scenario where escalation can
  override default budget denial behavior.

## 4) Edge Cases Visible In Sample Data

| Request | Edge Case | Why It Matters |
|---|---|---|
| REQ-010 | Budget overage plus near-director threshold | Tests escalation override behavior vs strict POL-008 denial. |
| REQ-014 | 47,500 USD near 50,000 threshold | Tests proactive governance escalation before threshold crossing. |
| REQ-015 | Ambiguous outcome in unrestricted category | Tests whether agent is permissive or conservative when no explicit violation exists. |
| REQ-012 | Staffing above 40 hours but contracted vendor | Validates POL-007 is conditional, not blanket staffing denial. |
| REQ-008 | Non-contracted vendor with contracted alternatives above threshold | Tests full POL-001 logic including amount and category scope. |
| REQ-009 | Catering request at low dollar value | Confirms absolute prohibition independent of amount. |

Additional data-shape edge case:

- Budgets use field name remaining. Implementations must read this key exactly
  when computing budget sufficiency.

## Request To Expected Outcome Pattern

| Request ID | Expected Outcome | Dominant Rationale Pattern |
|---|---|---|
| REQ-001 | approve | Active contracted vendor, within budget, no policy trigger. |
| REQ-002 | approve | Within budget and compliant; manager-range note only. |
| REQ-003 | approve | Active contract, low amount, clear budget headroom. |
| REQ-004 | approve | Within budget, below manager threshold cutoff by cents. |
| REQ-005 | approve | Contracted security vendor, within budget, no violations. |
| REQ-006 | deny | Budget overage against low remaining balance. |
| REQ-007 | deny | Expired contract vendor cannot be used. |
| REQ-008 | deny | Single-source restriction violation over 25,000 USD. |
| REQ-009 | deny | Catering category is prohibited. |
| REQ-010 | escalate | Overage plus near-director governance concern. |
| REQ-011 | escalate | Compliance-flagged vendor requires legal/compliance review. |
| REQ-012 | approve | Valid staffing contract and budget compliance. |
| REQ-013 | approve | Training category has no single-source restriction, within budget. |
| REQ-014 | escalate | Near-threshold escalation pattern for director visibility. |
| REQ-015 | ambiguous | No direct violation; behavior depends on agent conservatism. |

## Summary

The domain is policy-first, with budget and vendor controls enforcing most denials,
and governance/compliance signals driving escalations. Sample data intentionally
includes ambiguity and one policy-tension scenario (REQ-010) to test precedence
design in the agent decision policy.
