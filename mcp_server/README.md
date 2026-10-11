# Campus Customs MCP server

This read-only FastMCP server gives Campus Customs agents a controlled way to
retrieve facts from the current operational shop database. It uses only:

```text
data/campus_customs_new.db
```

The tools do not call external services, invent values, or modify the database.

All five HW5 agents use this same MCP boundary. No agent has a second direct
database-tools layer.

## Tools

- `get_ticket(ticket_id)`: reads a desk ticket and its linked invoice or lease IDs.
- `check_inventory_and_price(sku, size)`: reads `inventory` and `pricing` for stock, location, unit cost, and list price.
- `get_financial_context(ticket_id)`: reads linked `cash_accounts`, `invoices`, `vendors`, `leases`, and `payments` facts.

The server is not started as part of this problem. From the HW5 folder, a later
integration can run it with:

```sh
python -m mcp_server.server
```
