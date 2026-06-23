from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PurchaseRequest(BaseModel):
    request_id: NonEmptyStr
    requestor: NonEmptyStr
    cost_center_id: NonEmptyStr
    vendor_name: NonEmptyStr
    vendor_id: NonEmptyStr
    category: NonEmptyStr
    quantity: int
    unit_price: float = Field(ge=0)
    total_amount: float = Field(ge=0)


class ProcurementRecommendation(BaseModel):
    decision: Literal["approve", "deny", "escalate"]
    rationale: NonEmptyStr
