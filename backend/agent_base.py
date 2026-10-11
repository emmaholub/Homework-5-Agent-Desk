from __future__ import annotations

from .audit import record
from .models import AgentFinding, AgentRequest, AuditEvent


MAX_STEPS = 6
MAX_DELEGATIONS = 4
MAX_CUSTOMER_RECORDS = 1
MAX_MONEY_FACTS = 12


def audit(agent: str, step: int, action: str, arguments: dict, result: str, stop_reason: str) -> None:
    record(AuditEvent(timestamp="", agent=agent, step=step, action=action, arguments=arguments, result=result[:500], stop_reason=stop_reason))


def safe_customer_args(request: AgentRequest) -> dict:
    return {"user_id": request.customer.user_id} if request.customer.user_id else {}


def blocked(agent: str, reason: str) -> AgentFinding:
    return AgentFinding(agent=agent, status="blocked", answer=reason)
