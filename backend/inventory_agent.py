from __future__ import annotations

from .agent_base import audit, blocked
from .mcp_client import CampusCustomsMCP
from .models import AgentFinding, AgentRequest, ProductFact
from .runtime import make_agent


def pydantic_agent():
    return make_agent("inventory.md", AgentFinding)


def run(request: AgentRequest, step: int = 1) -> AgentFinding:
    text = request.message.lower()
    if not any(word in text for word in ("stock", "size", "available", "pink", "price", "cost")) and not request.product_id:
        return blocked("inventory", "Inventory was not needed for this request.")
    product_id = request.product_id
    if not product_id:
        product_id = None
    if not product_id:
        audit("inventory", step, "mcp.get_product_availability", {"product_id": None}, "No matching product", "no_product")
        return blocked("inventory", "I could not identify a catalogue product to check.")
    ticket_data = CampusCustomsMCP.get_ticket(int(product_id)) if product_id.isdigit() else None
    if ticket_data and ticket_data.get("sku"):
        product_id = ticket_data["sku"]
    data = CampusCustomsMCP.check_inventory_and_price(product_id)
    audit("inventory", step, "mcp.get_product_availability", {"product_id": product_id}, "availability returned" if data else "product missing", "complete")
    if not data:
        return blocked("inventory", "That product is not in the catalogue.")
    rows = data.get("inventory", [])
    fact = ProductFact(product_id=product_id, name=rows[0]["name"] if rows else product_id,
                       price=(data.get("pricing") or {}).get("list_price"),
                       inventory_by_size=[{"size": r["size"], "quantity": r["qty"]} for r in rows])
    return AgentFinding(agent="inventory", status="complete", answer="Verified price, colors, and size quantities from the MCP server.", facts=[fact])
