"""Procurement Intelligence Agent definition and deterministic evaluator."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()
_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

_SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

You MUST evaluate each request with all four tools:
1) check_budget(cost_center_id, total_amount)
2) check_vendor_duplication(vendor_id, category, total_amount)
3) check_policy_compliance(request)
4) assess_risk(vendor_id)

You MUST enforce decision priority exactly as:
escalate > deny > approve

Decision constraints:
- Final decision MUST be one of: approve, deny, escalate.
- Rationale MUST be non-empty and evidence-based.
- Rationale MUST cite triggered checks and concrete facts (policy IDs, thresholds,
  overage, conflict IDs, risk level) when available.

Error handling constraints:
- If any tool returns an error field or cannot complete, treat the request as
  safety-incomplete and return decision escalate.
- Include the tool error context in rationale.
""".strip()

# Keep Anthropic Pydantic AI agent definition as specified for project architecture.
agent: Agent[None, ProcurementRecommendation] | None
try:
    if _ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = _ANTHROPIC_API_KEY
        agent = Agent(
            model="anthropic:claude-3-5-haiku-latest",
            output_type=ProcurementRecommendation,
            system_prompt=_SYSTEM_PROMPT,
            tools=[
                check_budget,
                check_vendor_duplication,
                check_policy_compliance,
                assess_risk,
            ],
        )
    else:
        agent = None
except Exception:
    agent = None


def evaluate_purchase_request(request: PurchaseRequest) -> ProcurementRecommendation:
    """Evaluate one request using all four tools and decision precedence rules.

    This deterministic path is used for reliable local verification and tests.
    It calls all four tools for every request and applies escalate > deny > approve.
    """
    budget_result = check_budget(request.cost_center_id, request.total_amount)
    duplication_result = check_vendor_duplication(
        request.vendor_id,
        request.category,
        request.total_amount,
    )
    compliance_result = check_policy_compliance(request)
    risk_result = assess_risk(request.vendor_id)

    errors: list[str] = []
    if "error" in budget_result:
        errors.append(f"check_budget: {budget_result['error']}")
    if "error" in duplication_result:
        errors.append(f"check_vendor_duplication: {duplication_result['error']}")
    if "error" in compliance_result:
        errors.append(f"check_policy_compliance: {compliance_result['error']}")
    if "error" in risk_result:
        errors.append(f"assess_risk: {risk_result['error']}")

    if errors:
        rationale = (
            "Escalated because one or more checks failed to complete safely: "
            + "; ".join(errors)
        )
        return ProcurementRecommendation(decision="escalate", rationale=rationale)

    policy_violations = compliance_result.get("violations", [])
    forced_escalations = [
        v for v in policy_violations if v.get("forced_decision") == "escalate"
    ]
    forced_denials = [
        v for v in policy_violations if v.get("forced_decision") == "deny"
    ]

    risk_level = str(risk_result.get("risk_level", "low"))
    overage = float(budget_result.get("overage", 0.0))
    duplication_violation = bool(duplication_result.get("violation", False))
    near_director_threshold = 47_500.0 <= request.total_amount < 50_000.0

    blocking_escalations = [
        v for v in forced_escalations if str(v.get("policy_id")) != "POL-002"
    ]

    if blocking_escalations or risk_level == "critical" or near_director_threshold:
        evidence: list[str] = []
        if blocking_escalations:
            ids = ", ".join(str(v.get("policy_id")) for v in blocking_escalations)
            evidence.append(f"escalation policy trigger(s): {ids}")
        if risk_level == "critical":
            evidence.append("risk assessment returned critical")
        if near_director_threshold:
            evidence.append(
                f"amount ${request.total_amount:,.2f} is within 5% of $50,000 threshold"
            )
        rationale = "Escalated due to " + "; ".join(evidence) + "."
        return ProcurementRecommendation(decision="escalate", rationale=rationale)

    if (
        overage > 0.0
        or duplication_violation
        or forced_denials
        or risk_level == "high"
    ):
        evidence = []
        if overage > 0.0:
            evidence.append(
                f"budget overage of ${overage:,.2f} for cost center {request.cost_center_id}"
            )
        if duplication_violation:
            conflicts = duplication_result.get("conflicting_active_vendor_ids", [])
            evidence.append(f"POL-001 single-source conflict with vendor(s): {conflicts}")
        if forced_denials:
            ids = ", ".join(str(v.get("policy_id")) for v in forced_denials)
            evidence.append(f"policy denial trigger(s): {ids}")
        if risk_level == "high":
            evidence.append("risk assessment returned high")
        rationale = "Denied due to " + "; ".join(evidence) + "."
        return ProcurementRecommendation(decision="deny", rationale=rationale)

    rationale = (
        "Approved: all four checks completed with no escalation or denial triggers; "
        f"budget overage is ${overage:,.2f} and risk level is {risk_level}."
    )
    return ProcurementRecommendation(decision="approve", rationale=rationale)