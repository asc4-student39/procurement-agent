## ADDED Requirements

### Requirement: Centralized procurement data access
The system MUST provide loader functions in data/loader.py for budgets, vendors, policies, and sample requests, and these functions SHALL be the canonical source for mock dataset retrieval.

#### Scenario: Tool reads budgets through loader
- **WHEN** a budget check tool needs remaining budget for a cost center
- **THEN** it obtains budget records via data/loader.py rather than direct file access

### Requirement: No direct mock_data reads in tool and agent logic
Tool modules and agent orchestration MUST NOT read files under mock_data/ directly and SHALL rely exclusively on data/loader.py for reference data.

#### Scenario: Direct file read prevented by tests
- **WHEN** test inspection evaluates tool and agent modules for direct mock_data path reads
- **THEN** the tests confirm access occurs through loader abstractions only

### Requirement: Loader error transparency
Loader failures MUST be surfaced to callers with explicit error context so tool and agent layers can include the failure in rationale and select safe escalation.

#### Scenario: Missing data source reported
- **WHEN** loader cannot retrieve a required dataset
- **THEN** the caller receives explicit error information suitable for rationale inclusion
