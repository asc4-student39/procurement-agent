from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def _make_request(
    request_id: str,
    vendor_id: str,
    vendor_name: str,
    category: str,
    total_amount: float,
    quantity: int = 1,
    cost_center_id: str = "CC-001",
) -> PurchaseRequest:
    return PurchaseRequest(
        request_id=request_id,
        requestor="Test User",
        cost_center_id=cost_center_id,
        vendor_name=vendor_name,
        vendor_id=vendor_id,
        category=category,
        quantity=quantity,
        unit_price=total_amount,
        total_amount=total_amount,
    )


def test_pol_004_catering_prohibition_returns_deny() -> None:
    request = _make_request(
        request_id="REQ-009",
        vendor_id="V-017",
        vendor_name="Summit Catering Co.",
        category="catering",
        total_amount=3200.0,
        quantity=1,
        cost_center_id="CC-005",
    )

    result = check_policy_compliance(request)

    pol004 = next(v for v in result["violations"] if v["policy_id"] == "POL-004")
    assert pol004["forced_decision"] == "deny"
    assert pol004["rule_description"]


def test_pol_002_manager_threshold_is_reported() -> None:
    request = _make_request(
        request_id="REQ-MGR-001",
        vendor_id="V-005",
        vendor_name="Pinnacle Hardware",
        category="hardware",
        total_amount=12000.0,
        quantity=1,
        cost_center_id="CC-004",
    )

    result = check_policy_compliance(request)

    pol002 = next(v for v in result["violations"] if v["policy_id"] == "POL-002")
    assert pol002["forced_decision"] == "escalate"
    assert pol002["rule_description"]


def test_pol_005_expired_contract_vendor_returns_deny() -> None:
    request = _make_request(
        request_id="REQ-007",
        vendor_id="V-010",
        vendor_name="Crestview Print and Media",
        category="marketing_materials",
        total_amount=5400.0,
        quantity=1,
        cost_center_id="CC-010",
    )

    result = check_policy_compliance(request)

    pol005 = next(v for v in result["violations"] if v["policy_id"] == "POL-005")
    assert pol005["forced_decision"] == "deny"
    assert pol005["rule_description"]