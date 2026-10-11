# AI Prompts Log – HW5: Campus Customs Multi-Agent Operations

## Problem 1: Vibe coder prompts
**Prompt:** Create `AI_prompts.md` on day one and record each problem number/title, my prompt, any follow-up, and what the first prompt missed.
**Follow-up:** Replace placeholders with the actual prompts used for Problems 2–9.
**What was lacking after the first prompt:** The initial file had headings but no actual prompt record.

## Problem 2: Study the database
**Prompt:** Inspect every table and column in `data/campus_customs.db`, copy it to `data/campus_customs_new.db`, trace tickets 101–103 through their links, and start `output/harness.md` with fields and agent relevance. Never modify the original.
**Follow-up:** Verify the copy and document ticket links to inventory, pricing, leases, invoices, vendors, and cash.
**What was lacking after the first prompt:** The schema summary needed ticket-specific relationships and copy verification.

## Problem 3: Build the MCP server
**Prompt:** Build a read-only FastMCP server against `data/campus_customs_new.db` with `get_ticket`, `check_inventory_and_price`, and `get_financial_context`; document each tool's tables, ticket, and specific purpose in `harness.md` and `mcp_server/README.md`.
**Follow-up:** Ensure every tool returns database facts only and that financial context joins the rent ticket to lease, invoice/vendor, cash, and payments.
**What was lacking after the first prompt:** Read-only behavior and exact ticket links needed to be explicit.

## Problem 4: Connect and test MCP
**Prompt:** Add the MCP connection JSON at the project root and call all three ticket tools. Save `output/MCP_smoke.json` with each prompt, exact tool name, and real database output.
**Follow-up:** Replace stale product/user smoke examples with evidence from the three current ticket tools.
**What was lacking after the first prompt:** The earlier smoke file did not match the current MCP server.

## Problem 5: Build the five-agent team
**Prompt:** Build Boss, Inventory, Accounting, Facilities, and Customer Service with PydanticAI, one detailed prompt each under `backend/prompts/`, typed models in `backend/models.py`, Portkey `gpt-6-luna` using `PORTKEY_API_KEY`, MCP-only shop facts, bounded handoffs, and append-only audit events.
**Follow-up:** Add blocked outcomes for unnecessary agents, customer/money limits, and payment guardrails: agents prepare but never move money.
**What was lacking after the first prompt:** Safety limits and auditable blocked steps were not explicit.

## Problem 6: Plan the tickets
**Prompt:** Create a double-clickable `output/desk_tickets.html` with tabs 101, 102, 103, Cash, and Reflection. Write selective Expected plans covering Boss's first call, handoffs, and MCP tools; leave Actual blank until execution.
**Follow-up:** Route 101 to Customer Service/Inventory, 102 to Facilities/Accounting, and 103 to Customer Service/Inventory/Accounting.
**What was lacking after the first prompt:** The plan needed selective, ticket-specific agent routing.

## Problem 7: FastAPI backend routes
**Prompt:** Add routes for tickets, running a ticket, activity, human-only payment approval, checking balance, and reset. Use MCP for shop facts, require explicit approval before payment, cap amounts, and document routes in `harness.md`.
**Follow-up:** Return findings and tool names, and restore the copied data pack's starting balance on reset.
**What was lacking after the first prompt:** Money guardrails and inspectable tool evidence needed to be specified.

## Problem 8: React dashboard
**Prompt:** Build a creative React/Vite/TypeScript dashboard that lists/selects/runs tickets, shows agent progress and summaries, displays activity, provides a human Approve button, and refreshes cash after payment. Allow local frontend ports through CORS and document design choices.
**Follow-up:** Support both 5173 and Vite fallback port 5176, and show a useful failure state rather than silently showing zero when the API is down.
**What was lacking after the first prompt:** Fallback ports and backend failure feedback were missing.

## Problem 9: Run and document all tickets
**Prompt:** Reset the working copy, record starting balance, run 101–103, fill Actual beside Expected, document cash changes and database-matching ending balance, and save `resolved_tickets.json`, `resolved_board.html`, and append-only audit evidence.
**Follow-up:** Verify the ending balance directly from `cash_accounts` and explicitly record each ticket's agents, tools, outcome, and approvals.
**What was lacking after the first prompt:** Evidence needed direct database verification, not only dashboard text.

## Problems 10–11
No additional requirements were supplied for these HW5 problems; no prompts are fabricated here.
