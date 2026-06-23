from tools.vendor_duplication import check_vendor_duplication


def test_req_008_vendor_duplication_conflicts() -> None:
    result = check_vendor_duplication(
        vendor_id="V-012",
        category="office_supplies",
        requested_amount=28_500.0,
    )

    assert result["violation"] is True
    assert result["threshold_applies"] is True
    assert result["category_covered"] is True
    assert set(result["conflicting_active_vendor_ids"]) == {"V-001", "V-003"}
