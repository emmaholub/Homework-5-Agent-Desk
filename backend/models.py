from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CustomerContext(BaseModel):
    user_id: int | None = None
    name: str | None = None
    email: str | None = None


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    customer: CustomerContext = Field(default_factory=CustomerContext)
    product_id: str | None = None
    ticket_id: int | None = None


class ProductFact(BaseModel):
    product_id: str
    name: str
    price: float | None = None
    colors: list[str] = Field(default_factory=list)
    inventory_by_size: list[dict[str, int | str]] = Field(default_factory=list)


class AgentFinding(BaseModel):
    agent: str
    status: Literal["complete", "blocked", "delegated", "partial"]
    answer: str
    facts: list[ProductFact] = Field(default_factory=list)
    next_agent: str | None = None


class AgentRun(BaseModel):
    request: AgentRequest
    findings: list[AgentFinding] = Field(default_factory=list)
    final_answer: str = ""
    stop_reason: str = ""


class AuditEvent(BaseModel):
    timestamp: str
    agent: str
    step: int
    action: str
    arguments: dict
    result: str
    stop_reason: str
