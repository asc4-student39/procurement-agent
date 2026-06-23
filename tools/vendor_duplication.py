"""Vendor duplication and POL-001 single-source policy check tool."""

from __future__ import annotations

from data.loader import load_policies, load_vendors


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    requested_amount: float = 0.0,
) -> dict[str, object]:
    """Evaluate vendor duplication conflicts and POL-001 single-source violations.

    This tool finds active contracted vendors in the provided category and
    applies POL-001 threshold logic. POL-001 violations are only triggered when
    requested_amount is greater than the policy threshold and the category is
    covered by POL-001.

    Args:
        vendor_id: Requested vendor identifier.
        category: Requested purchase category.
        requested_amount: Total request amount used for POL-001 threshold gating.

    Returns:
        A structured result containing:
        - violation: Whether POL-001 is violated.
        - conflicting_active_vendor_ids: Active vendor IDs in the same category,
          excluding the requested vendor.
        - policy_id: The policy used for this check (POL-001).
        - threshold_amount: POL-001 threshold amount.
        - threshold_applies: Whether requested_amount exceeds threshold.
        - category_covered: Whether category is included in POL-001 categories.
        - error: Present when loader access fails or policy data is unavailable.
    """
    try:
        vendors = load_vendors()
        policies = load_policies()
    except Exception as exc:  # pragma: no cover - defensive safety path
        return {
            "violation": False,
            "conflicting_active_vendor_ids": [],
            "policy_id": "POL-001",
            "threshold_amount": 25_000.0,
            "threshold_applies": requested_amount > 25_000.0,
            "category_covered": False,
            "error": f"Unable to load policy/vendor data: {exc}",
        }

    pol001 = next(
        (policy for policy in policies if policy.get("policy_id") == "POL-001"),
        None,
    )

    if pol001 is None:
        return {
            "violation": False,
            "conflicting_active_vendor_ids": [],
            "policy_id": "POL-001",
            "threshold_amount": 25_000.0,
            "threshold_applies": requested_amount > 25_000.0,
            "category_covered": False,
            "error": "POL-001 was not found in policy data.",
        }

    threshold_amount = float(pol001.get("threshold_amount", 25_000.0))
    affected_categories_raw = pol001.get("affected_categories", [])
    affected_categories = {
        str(item) for item in affected_categories_raw if isinstance(item, str)
    }

    category_covered = category in affected_categories
    threshold_applies = requested_amount > threshold_amount

    conflicting_active_vendor_ids = [
        str(vendor.get("vendor_id"))
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == category
        and vendor.get("contract_status") == "active"
    ]

    requested_vendor = next(
        (vendor for vendor in vendors if vendor.get("vendor_id") == vendor_id),
        None,
    )
    requested_vendor_is_active_in_category = bool(
        requested_vendor
        and requested_vendor.get("category") == category
        and requested_vendor.get("contract_status") == "active"
    )

    violation = bool(
        threshold_applies
        and category_covered
        and conflicting_active_vendor_ids
        and not requested_vendor_is_active_in_category
    )

    return {
        "violation": violation,
        "conflicting_active_vendor_ids": conflicting_active_vendor_ids,
        "policy_id": "POL-001",
        "threshold_amount": threshold_amount,
        "threshold_applies": threshold_applies,
        "category_covered": category_covered,
    }