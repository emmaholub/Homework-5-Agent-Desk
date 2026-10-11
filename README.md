# Campus Customs — Homeworks 5

This repository contains a Campus Customs operations desk with a read-only
FastMCP shop-data boundary, five bounded agents, a FastAPI backend, and a React
dashboard. The two SQLite files in `data/` are intentionally included for this
assignment:

- `data/campus_customs.db` — original seed database; do not modify it.
- `data/campus_customs_new.db` — working copy used by MCP and the application.

Never commit `.env` or a real Portkey key. Use `.env.example` as the template.

## Reset before a full run

Reset the working copy through the backend before running all three tickets:

```sh
curl -X POST http://127.0.0.1:8000/reset
```

This restores tickets 101–103 to open, clears desk activity and payments, and
restores the checking balance to `$3,400.00`. The original database is never
changed. Confirm the balance with:

```sh
curl http://127.0.0.1:8000/cash/checking
```

## Start the MCP server

Use Python 3.10+ and install the pinned requirements first. The project uses
MCP 1.x because `mcp_server/server.py` uses `FastMCP`:

```sh
python3.12 -m venv .venv312
source .venv312/bin/activate
python -m pip install -r requirements.txt
python -m mcp_server.server
```

The MCP server reads only `data/campus_customs_new.db` and exposes
`get_ticket`, `check_inventory_and_price`, and `get_financial_context`. It does
not write shop data.

## Start the backend

From the project root, with the virtual environment active:

```sh
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API provides ticket, activity, payment-approval, balance, and reset routes.
Only the human approval route can move money.

## Start the dashboard

In a second Terminal window:

```sh
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the Terminal, usually
`http://localhost:5173/` (or a fallback port such as 5176). The dashboard
calls the backend, shows ticket-specific agent activity, and refreshes the
checking balance after a human payment approval.

## Submission evidence

- `AI_prompts.md` records the nine HW5 prompt/follow-up sections.
- `output/harness.md` documents tables, tools, agents, routes, dashboard, and
  safety limits.
- `output/MCP_smoke.json` contains real outputs from all three MCP tools.
- `output/audit_trail.json` is append-only JSON Lines evidence.
- `output/desk_tickets.html` contains Expected, Actual, Cash, and Reflection
  tabs and can be opened by double-clicking it.
- `output/resolved_tickets.json` and `output/resolved_board.html` record the
  completed ticket run.
