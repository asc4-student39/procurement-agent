"""Policy compliance tool for evaluating purchase requests against procurement rules."""

from __future__ import annotations

from data.loader import load_budgets, load_policies, load_vendors
from models import PurchaseRequest


def _violation(policy_id: str, rule_description: str, forced_decision: str) -> dict[str, str]:
    """Build a normalized policy violation record."""
    return {
        "policy_id": policy_id,
        "rule_description": rule_description,
        "forced_decision": forced_decision,
    }


def check_policy_compliance(request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against all eight procurement policies.

    The evaluation loads policies, vendors, and budgets from ``data/loader.py``
    and returns every triggered policy violation. Each violation record includes
    ``policy_id``, ``rule_description``, and ``forced_decision`` (deny/escalate).

    Args:
        request: Purchase request being evaluated.

    Returns:
        A dictionary with:
        - ``violations``: List of triggered policy violations.
        - ``violation_count``: Count of triggered violations.
        - ``evaluated_policy_ids``: Policy IDs considered during evaluation.
        - ``error``: Present when policy data cannot be loaded.
    """
    try:
        policies = load_policies()
        vendors = load_vendors()
        budgets = load_budgets()
    except Exception as exc:  # pragma: no cover - defensive safety path
        return {
            "violations": [],
            "violation_count": 0,
            "evaluated_policy_ids": [],
            "error": f"Unable to evaluate policies: {exc}",
        }

    policy_by_id = {
        str(policy.get("policy_id")): policy
        for policy in policies
        if isinstance(policy.get("policy_id"), str)
    }
    evaluated_policy_ids = [
        policy_id for policy_id in [
            "POL-001",
            "POL-002",
            "POL-003",
            "POL-004",
            "POL-005",
            "POL-006",
            "POL-007",
            "POL-008",
        ]
        if policy_id in policy_by_id
    ]

    vendor = next(
        (v for v in vendors if v.get("vendor_id") == request.vendor_id),
        None,
    )
    budget = next(
        (b for b in budgets if b.get("cost_center_id") == request.cost_center_id),
        None,
    )

    violations: list[dict[str, str]] = []

    # POL-001: Single-source restriction over threshold in covered categories.
    pol001 = policy_by_id.get("POL-001")
    if pol001 is not None:
        threshold = float(pol001.get("threshold_amount", 25_000.0))
        affected_categories = {
            str(category)
            for category in pol001.get("affected_categories", [])
            if isinstance(category, str)
        }
        conflicting_active_vendor_ids = [
            str(v.get("vendor_id"))
            for v in vendors
            if v.get("vendor_id") != request.vendor_id
            and v.get("category") == request.category
            and v.get("contract_status") == "active"
        ]
        requested_vendor_is_active = bool(
            vendor
            and vendor.get("category") == request.category
            and vendor.get("contract_status") == "active"
        )
        if (
            request.total_amount > threshold
            and request.category in affected_categories
            and conflicting_active_vendor_ids
            and not requested_vendor_is_active
        ):
            violations.append(
                _violation(
                    "POL-001",
                    str(pol001.get("description", "Single-source restriction violated.")),
                    "deny",
                )
            )

    # POL-002: Manager approval threshold.
    pol002 = policy_by_id.get("POL-002")
    if pol002 is not None:
        low = float(pol002.get("threshold_amount", 10_000.0))
        high = float(pol002.get("upper_threshold", 49_999.99))
        if low <= request.total_amount <= high:
            violations.append(
                _violation(
                    "POL-002",
                    str(pol002.get("description", "Manager approval threshold triggered.")),
                    "escalate",
                )
            )

    # POL-003: Director approval threshold.
    pol003 = policy_by_id.get("POL-003")
    if pol003 is not None:
        threshold = float(pol003.get("threshold_amount", 50_000.0))
        if request.total_amount >= threshold:
            violations.append(
                _violation(
                    "POL-003",
                    str(pol003.get("description", "Director approval threshold triggered.")),
                    "escalate",
                )
            )

    # POL-004: Prohibited category.
    pol004 = policy_by_id.get("POL-004")
    if pol004 is not None:
        prohibited_categories = {
            str(category)
            for category in pol004.get("affected_categories", [])
            if isinstance(category, str)
        }
        if request.category in prohibited_categories:
            violations.append(
                _violation(
                    "POL-004",
                    str(pol004.get("description", "Category is prohibited.")),
                    "deny",
                )
            )

    # POL-005: Expired contract vendor.
    pol005 = policy_by_id.get("POL-005")
    if pol005 is not None and vendor and vendor.get("contract_status") == "expired":
        violations.append(
            _violation(
                "POL-005",
                str(pol005.get("description", "Vendor contract is expired.")),
                "deny",
            )
        )

    # POL-006: Compliance-flagged vendor hold.
    pol006 = policy_by_id.get("POL-006")
    if pol006 is not None and vendor and bool(vendor.get("compliance_flag")):
        violations.append(
            _violation(
                "POL-006",
                str(pol006.get("description", "Vendor has active compliance flag.")),
                "escalate",
            )
        )

    # POL-007: Staffing vendor single-source for > 40 hour engagements.
    pol007 = policy_by_id.get("POL-007")
    if pol007 is not None:
        staffing_categories = {
            str(category)
            for category in pol007.get("affected_categories", [])
            if isinstance(category, str)
        }
        if request.category in staffing_categories and request.quantity > 40:
            vendor_is_active_staffing = bool(
                vendor
                and vendor.get("category") == request.category
                and vendor.get("contract_status") == "active"
            )
            if not vendor_is_active_staffing:
                violations.append(
                    _violation(
                        "POL-007",
                        str(pol007.get("description", "Staffing single-source rule violated.")),
                        "deny",
                    )
                )

    # POL-008: Budget overage prohibition.
    pol008 = policy_by_id.get("POL-008")
    if pol008 is not None and budget is not None:
        remaining = float(budget.get("remaining", 0.0))
        if request.total_amount > remaining:
            violations.append(
                _violation(
                    "POL-008",
                    str(pol008.get("description", "Request exceeds remaining budget.")),
                    "deny",
                )
            )

    return {
        "violations": violations,
        "violation_count": len(violations),
        "evaluated_policy_ids": evaluated_policy_ids,
    }