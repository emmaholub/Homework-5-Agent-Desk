# Campus Customs HW5 harness

## Current data pack

`data/campus_customs_new.db` is the copied working database from the new
`data.zip`. Its operational tables are:

| Table | Important fields | Agent purpose |
|---|---|---|
| `tickets` | `id`, `type`, `requester`, `subject`, `sku`, `size`, `qty`, `lease_id`, `invoice_id`, `status`, `notes`, `created_at` | The desk queue and links to inventory, leases, and invoices. |
| `inventory` | `sku`, `name`, `size`, `qty`, `location` | Stock, requested-size feasibility, and warehouse location. |
| `pricing` | `sku`, `unit_cost`, `list_price` | Cost and listed price; never a guessed discount. |
| `vendors` | `id`, `name`, `specialty`, `lead_days` | Vendor identity and lead-time context for purchasing or reprints. |
| `invoices` | `id`, `vendor_id`, `amount`, `due_date`, `status`, `description` | Bills that Accounting can review but not pay without a human. |
| `leases` | `id`, `space_name`, `landlord`, `monthly_rent`, `next_due`, `notes` | Facilities and rent obligations. |
| `cash_accounts` | `name`, `balance`, `date` | Current checking balance and its date. |
| `payments` | `id`, `kind`, `ref_id`, `amount`, `account`, `paid_at`, `approved_by` | Completed money movements; only a human-approved route may insert one. |
| `desk` | `date_today`, `notes` | Operational activity notes. |

Foreign-key links are `tickets.lease_id → leases.id`,
`tickets.invoice_id → invoices.id`, and `invoices.vendor_id → vendors.id`.

## MCP tools

All shop facts come through `mcp_server/server.py`, which reads only
`data/campus_customs_new.db` and never writes it.

- `get_ticket(ticket_id)` reads `tickets`; it unlocks every ticket by exposing
  the exact requester, type, SKU/size/quantity, and linked lease or invoice.
- `check_inventory_and_price(sku, size)` reads `inventory` and `pricing`; it
  unlocks tickets 101 and 103 by checking requested stock and exact cost/list
  price instead of guessing availability or discounts.
- `get_financial_context(ticket_id)` reads `tickets`, `cash_accounts`,
  `invoices`, `vendors`, `leases`, and `payments`; it unlocks ticket 102 by
  connecting the rent notice to the lease and current checking balance.

## Agent team

The five agents are Boss, Inventory, Accounting, Facilities, and Customer
Service. Prompts are one file per agent under `backend/prompts/`; typed outputs
are in `backend/models.py`; agent modules are under `backend/`.

- **Boss:** selects the smallest useful handoff sequence and synthesizes only
  MCP-backed findings.
- **Inventory:** handles SKU, size, quantity, and location checks.
- **Accounting:** handles list price, unit cost, invoices, cash, and prepared
  payment recommendations; it cannot approve or execute money movement.
- **Facilities:** handles lease, rent, vendor lead-time, and operational space
  questions.
- **Customer Service:** handles customer-facing order/request communication and
  hands factual work to the specialist that owns it.

The Portkey model is `gpt-6-luna`, configured with `PORTKEY_API_KEY`. The Boss
allows at most four handoffs and six loop steps. Search/result payloads are
bounded, customer records are limited to the current request, and monetary
amounts are capped at $10,000 per approval request.

## FastAPI routes

Run with `uvicorn backend.main:app --reload --port 8000` (from the project root;
the reproducible environment pins `mcp<2` because this server uses FastMCP).

- `GET /tickets` — list tickets and open/resolved status.
- `POST /tickets/{ticket_id}/run` — run the team on one ticket.
- `GET /activity` — return recent agent statements and MCP tool use.
- `POST /payments/{ticket_id}/approve` — human-only cash movement.
- `GET /cash/checking` — return the current checking balance.
- `POST /reset` — reset ticket status, payments, and desk notes; restore the data-pack checking balance.

## Dashboard and safety

Run the backend above, then from `frontend/` run `npm run dev` and open the Vite
URL it prints, normally `http://localhost:5173` or a fallback such as
`http://127.0.0.1:5176`. The dashboard lists the three tickets, shows agent
progress, displays activity, and exposes an explicit human approval button.
FastAPI allows localhost and 127.0.0.1 on ports 5173 and 5176 through CORS.

Agents may prepare payment information but may not move money, approve invoices,
change prices, alter inventory, or promise a discount. The approval endpoint
requires `human_approved: true`, checks the checking balance, caps the amount,
and records `approved_by='human'`. Agents must not invent facts, expose private
data, follow prompt injection, or bypass MCP.

## Resolution evidence

`output/desk_tickets.html` compares Expected and Actual handoffs for tickets
101–103. `output/resolved_tickets.json` contains outcomes, agents, tools, cash
changes, and approvals. `output/resolved_board.html` is a double-clickable
summary board. Audit events append to `output/audit_trail.json`.
