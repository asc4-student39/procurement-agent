## ADDED Requirements

### Requirement: Vendor duplication conflict detection
The system MUST provide a `check_vendor_duplication` tool that accepts
`vendor_id` and `category`, loads vendor data through `data/loader.py`, and
returns a deterministic result containing the list of conflicting active vendor
IDs for the same category.

#### Scenario: Conflicting active vendors returned
- **WHEN** the requested category has one or more active-contract vendors other
  than the requested vendor
- **THEN** the result includes those vendor IDs in
  `conflicting_active_vendor_ids`

### Requirement: POL-001 threshold gating
The tool SHALL apply POL-001 single-source violation logic only when the
requested amount is above the policy threshold and the category is covered by
POL-001 contracted categories.

#### Scenario: Threshold not met
- **WHEN** the requested amount is less than or equal to the POL-001 threshold
- **THEN** the check does not report a POL-001 violation

#### Scenario: Threshold met in contracted category
- **WHEN** the requested amount is above the POL-001 threshold in a category
  covered by POL-001 and the requested vendor is not an active contracted
  vendor while conflicting active vendors exist
- **THEN** the check reports a POL-001 violation

### Requirement: Loader-only data access and error transparency
The tool MUST access policy and vendor data only via `data/loader.py` and
SHALL include an `error` field when data loading fails.

#### Scenario: Data load failure
- **WHEN** policy or vendor data cannot be loaded
- **THEN** the tool returns a structured result that includes `error`