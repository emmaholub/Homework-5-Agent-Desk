from __future__ import annotations

from .agent_base import audit, blocked
from .mcp_client import CampusCustomsMCP
from .models import AgentFinding, AgentRequest
from .runtime import make_agent


def pydantic_agent():
    return make_agent("facilities.md", AgentFinding)


def run(request: AgentRequest, step: int = 1) -> AgentFinding:
    if not request.ticket_id and not any(word in request.message.lower() for word in ("where", "pickup", "store", "hours", "facility", "location", "rent", "lease")):
        return blocked("facilities", "Facilities was not needed for this request.")
    if request.ticket_id and ("rent" in request.message.lower() or "lease" in request.message.lower()):
        data = CampusCustomsMCP.get_financial_context(request.ticket_id)
        lease = data.get("lease") or {}
        audit("facilities", step, "mcp.get_financial_context", {"ticket_id": request.ticket_id}, "linked lease facts returned", "complete")
        if not lease:
            return blocked("facilities", "No linked lease was found in the MCP data.")
        return AgentFinding(agent="facilities", status="complete", answer=f"Verified the {lease.get('space_name', 'shop')} lease with {lease.get('landlord', 'the landlord')}; next due date is {lease.get('next_due')}.")
    audit("facilities", step, "source capability check", {"requested": request.message[:120]}, "no facilities location table", "source_unavailable")
    return AgentFinding(agent="facilities", status="blocked", answer="The current shop database does not contain verified store-location or hours information.")
