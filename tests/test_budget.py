from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc_003() -> None:
    within_budget_result = check_budget("CC-003", 6800.0)

    assert within_budget_result["within_budget"] is True
    assert within_budget_result["remaining_budget"] == 6900.0
    assert within_budget_result["overage"] == 0.0

    over_budget_result = check_budget("CC-003", 8500.0)

    assert over_budget_result["within_budget"] is False
    assert over_budget_result["remaining_budget"] == 6900.0
    assert over_budget_result["overage"] == 1600.0
