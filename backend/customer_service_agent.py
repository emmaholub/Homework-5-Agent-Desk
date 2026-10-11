from __future__ import annotations

from .agent_base import audit, safe_customer_args, blocked
from .mcp_client import CampusCustomsMCP
from .models import AgentFinding, AgentRequest
from .runtime import make_agent


def pydantic_agent():
    return make_agent("customer_service.md", AgentFinding)


def run(request: AgentRequest, step: int = 1) -> AgentFinding:
    audit("customer_service", step, "customer context", safe_customer_args(request), "requester context received", "complete")
    name = request.customer.name or "there"
    return AgentFinding(agent="customer_service", status="complete", answer=f"I can help you, {name}, with verified Campus Customs information.")
