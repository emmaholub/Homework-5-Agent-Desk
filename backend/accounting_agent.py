from __future__ import annotations

from .agent_base import audit, blocked
from .mcp_client import CampusCustomsMCP
from .models import AgentFinding, AgentRequest, ProductFact
from .runtime import make_agent


def pydantic_agent():
    return make_agent("accounting.md", AgentFinding)


def run(request: AgentRequest, step: int = 1) -> AgentFinding:
    if not any(word in request.message.lower() for word in ("price", "cost", "total", "refund", "money", "cheapest", "rent", "lease", "due")):
        return blocked("accounting", "Accounting was not needed for this request.")
    if request.ticket_id and ("rent" in request.message.lower() or "lease" in request.message.lower()):
        data = CampusCustomsMCP.get_financial_context(request.ticket_id)
        lease = data.get("lease") or {}
        audit("accounting", step, "mcp.get_financial_context", {"ticket_id": request.ticket_id}, "rent and checking facts reviewed", "complete")
        return AgentFinding(agent="accounting", status="complete", answer=f"Reviewed the linked lease and checking balance; human approval is still required for any payment. Rent listed: ${lease.get('monthly_rent', 0):.2f}.")
    if not request.product_id:
        return blocked("accounting", "A ticket SKU is required before reading a price.")
    data = CampusCustomsMCP.check_inventory_and_price(request.product_id)
    pricing = data.get("pricing") or {}
    rows = data.get("inventory", [])
    facts = [ProductFact(product_id=request.product_id, name=rows[0]["name"] if rows else request.product_id,
                         price=pricing.get("list_price"))]
    audit("accounting", step, "mcp.check_inventory_and_price", {"sku": request.product_id}, "one price record", "complete")
    if not facts:
        return blocked("accounting", "No matching catalogue price was found.")
    return AgentFinding(agent="accounting", status="complete", answer="Prices were read from the catalogue; no payment or refund was performed.", facts=facts)
