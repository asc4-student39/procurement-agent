## 1. Model and Contract Setup

- [ ] 1.1 Implement or align PurchaseRequest Pydantic v2 model fields and validators in models.py
- [ ] 1.2 Implement or align ProcurementRecommendation model with decision constrained to approve/deny/escalate
- [ ] 1.3 Enforce non-empty rationale validation for recommendation output

## 2. Data Loader Foundations

- [ ] 2.1 Implement or align data/loader.py functions for budgets, vendors, policies, and requests datasets
- [ ] 2.2 Ensure loader returns deterministic structures and explicit error context on failures
- [ ] 2.3 Add tests proving tool and agent code paths use data/loader.py rather than direct mock_data access

## 3. Procurement Tool Implementation

- [ ] 3.1 Implement check_budget in tools/budget.py with within-budget and overage output
- [ ] 3.2 Implement check_vendor_duplication in tools/vendor_duplication.py for single-source policy checks
- [ ] 3.3 Implement check_policy_compliance in tools/policy_compliance.py for denial/escalation policy triggers
- [ ] 3.4 Implement assess_risk in tools/risk_assessment.py for contract/compliance risk classification
- [ ] 3.5 Add docstrings and type hints for all tool functions and outputs

## 4. Agent Orchestration and Decision Logic

- [ ] 4.1 Construct the Pydantic AI agent in agent.py with output_type set to ProcurementRecommendation
- [ ] 4.2 Wire agent toolset to call all four procurement checks for every request
- [ ] 4.3 Implement recommendation precedence logic: escalate > deny > approve
- [ ] 4.4 Implement error handling so tool failures are surfaced in rationale and force safe escalation
- [ ] 4.5 Ensure rationale references the checks and evidence driving each recommendation

## 5. Test Coverage and Verification

- [ ] 5.1 Add tool-level tests for primary success path of each tool under tests/
- [ ] 5.2 Add agent-level tests covering approve, deny, and escalate outcomes from sample requests
- [ ] 5.3 Add tests for edge cases including ambiguous or near-threshold scenarios and partial-data/tool-error paths
- [ ] 5.4 Run pytest tests/ -v --tb=short --junitxml=docs/test-results.xml and review failures

## 6. Spec and Delivery Readiness

- [ ] 6.1 Run openspec validate add-procurement-intelligence-agent and resolve validation issues
- [ ] 6.2 Confirm tasks map to implemented behavior and update checklist statuses during implementation
- [ ] 6.3 Prepare review summary linking model, loader, tool, and agent behavior to spec requirements
