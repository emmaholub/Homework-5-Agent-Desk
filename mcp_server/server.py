"""Read-only Campus Customs operations tools for the current HW5 data pack."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP

DATABASE = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
mcp = FastMCP("Campus Customs Operations")

def connect():
    c = sqlite3.connect(DATABASE); c.row_factory = sqlite3.Row; return c

@mcp.tool()
def get_ticket(ticket_id: int) -> dict[str, Any] | None:
    """Read one desk ticket and its linked invoice or lease context."""
    with connect() as c:
        row = c.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    return dict(row) if row else None

@mcp.tool()
def check_inventory_and_price(sku: str, size: str | None = None) -> dict[str, Any]:
    """Read stock/location and unit/list price for a SKU."""
    with connect() as c:
        stock = c.execute("SELECT * FROM inventory WHERE sku=? AND (? IS NULL OR size=?) ORDER BY size", (sku, size, size)).fetchall()
        price = c.execute("SELECT * FROM pricing WHERE sku=?", (sku,)).fetchone()
    return {"sku": sku, "inventory": [dict(r) for r in stock], "pricing": dict(price) if price else None}

@mcp.tool()
def get_financial_context(ticket_id: int) -> dict[str, Any]:
    """Read cash, invoice, lease, vendor, and payment facts relevant to a ticket."""
    with connect() as c:
        ticket = c.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
        cash = c.execute("SELECT * FROM cash_accounts WHERE name='checking'").fetchone()
        invoice = c.execute("SELECT i.*,v.name AS vendor_name,v.lead_days FROM invoices i LEFT JOIN vendors v ON v.id=i.vendor_id WHERE i.id=(SELECT invoice_id FROM tickets WHERE id=?)", (ticket_id,)).fetchone()
        lease = c.execute("SELECT * FROM leases WHERE id=(SELECT lease_id FROM tickets WHERE id=?)", (ticket_id,)).fetchone()
        payments = c.execute("SELECT * FROM payments WHERE ref_id=?", (ticket_id,)).fetchall()
    return {"ticket": dict(ticket) if ticket else None, "checking": dict(cash) if cash else None, "invoice": dict(invoice) if invoice else None, "lease": dict(lease) if lease else None, "payments": [dict(r) for r in payments]}

if __name__ == "__main__":
    mcp.run()
