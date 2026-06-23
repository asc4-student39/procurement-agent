"""Budget evaluation tool for procurement requests."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a request amount is within the cost center's remaining budget.

    Args:
        cost_center_id: The request's cost center identifier.
        requested_amount: The total amount requested for purchase.

    Returns:
        A structured result with the following keys:
        - within_budget: Whether requested_amount is less than or equal to the
          cost center's remaining budget.
        - remaining_budget: The remaining budget for the cost center.
        - overage: The positive amount above remaining budget, or 0.0 when within budget.

        If evaluation cannot complete, the result includes:
        - error: Human-readable error context.
    """
    try:
        budgets = load_budgets()
    except Exception as exc:  # pragma: no cover - defensive safety path
        return {
            "within_budget": False,
            "remaining_budget": 0.0,
            "overage": max(0.0, requested_amount),
            "error": f"Unable to load budget data: {exc}",
        }

    budget_record = next(
        (item for item in budgets if item.get("cost_center_id") == cost_center_id),
        None,
    )

    if budget_record is None:
        return {
            "within_budget": False,
            "remaining_budget": 0.0,
            "overage": max(0.0, requested_amount),
            "error": f"Cost center '{cost_center_id}' was not found.",
        }

    remaining_budget = float(budget_record.get("remaining", 0.0))
    overage = max(0.0, requested_amount - remaining_budget)

    return {
        "within_budget": overage == 0.0,
        "remaining_budget": remaining_budget,
        "overage": overage,
    }