"""Single shop-facts gateway.

In production this boundary is replaced by the configured FastMCP transport.
The imported functions are the MCP server tools themselves, not duplicate SQL
shop tools, so every agent uses the same database-backed tool contract.
"""

from mcp_server.server import check_inventory_and_price, get_financial_context, get_ticket


class CampusCustomsMCP:
    get_ticket = staticmethod(get_ticket)
    check_inventory_and_price = staticmethod(check_inventory_and_price)
    get_financial_context = staticmethod(get_financial_context)
