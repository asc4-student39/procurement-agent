"""Risk assessment tool for vendor-based procurement risk signals."""

from __future__ import annotations

from data.loader import load_vendors


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Assess procurement risk for the requested vendor.

    Args:
        vendor_id: Vendor identifier from the purchase request.

    Returns:
        A structured risk result with contract status and risk level.
        If evaluation cannot complete, the result includes an ``error`` field.
    """
    try:
        vendors = load_vendors()
    except Exception as exc:  # pragma: no cover - defensive safety path
        return {
            "vendor_id": vendor_id,
            "contract_status": "unknown",
            "compliance_flag": False,
            "risk_level": "critical",
            "risk_summary": "Vendor data unavailable.",
            "error": f"Unable to load vendor data: {exc}",
        }

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return {
            "vendor_id": vendor_id,
            "contract_status": "unknown",
            "compliance_flag": False,
            "risk_level": "high",
            "risk_summary": "Vendor not found in approved vendor data.",
            "error": f"Vendor '{vendor_id}' not found.",
        }

    contract_status = str(vendor.get("contract_status", "none"))
    compliance_flag = bool(vendor.get("compliance_flag", False))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = "Active compliance flag requires escalation."
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no active contract."
    else:
        risk_level = "low"
        risk_summary = "Vendor has active contract with no compliance flag."

    return {
        "vendor_id": vendor_id,
        "contract_status": contract_status,
        "compliance_flag": compliance_flag,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }