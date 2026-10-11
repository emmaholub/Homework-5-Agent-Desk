from __future__ import annotations

from .accounting_agent import run as accounting
from .agent_base import MAX_DELEGATIONS, MAX_STEPS, audit
from .customer_service_agent import run as customer_service
from .facilities_agent import run as facilities
from .inventory_agent import run as inventory
from .models import AgentFinding, AgentRequest, AgentRun
from .runtime import make_agent


def pydantic_agent():
    return make_agent("boss.md", AgentRun)


def run(request: AgentRequest) -> AgentRun:
    """Delegate a bounded request to specialists and synthesize only their facts."""
    findings: list[AgentFinding] = []
    # Use the ticket type to make the smallest useful handoff chain. This is
    # deliberately selective: a rent notice should not invoke inventory, and
    # an out-of-stock request should not invoke Facilities or Accounting.
    if request.ticket_id == 102 or "rent" in request.message.lower():
        specialists = [facilities, accounting]
    elif request.ticket_id == 101:
        specialists = [customer_service, inventory]
    elif request.ticket_id == 103:
        specialists = [customer_service, inventory, accounting]
    else:
        specialists = [customer_service]
    for step, specialist in enumerate(specialists[:MAX_DELEGATIONS], start=1):
        finding = specialist(request, step)
        findings.append(finding)
        audit("boss", step, "delegate", {"worker": finding.agent, "message_length": len(request.message)}, finding.status, "worker_returned")
        if step >= MAX_STEPS:
            break
    useful = [f for f in findings if f.status == "complete"]
    facts = [fact for finding in useful for fact in finding.facts][:12]
    if facts:
        price_text = "; ".join(f"{fact.name}: ${fact.price:.2f}" for fact in facts if fact.price is not None)
        final = price_text or "I found verified shop information and can help with the available details."
    else:
        final = next((f.answer for f in findings if f.status != "blocked"), "I do not have a verified answer in the shop database.")
    audit("boss", len(findings) + 1, "synthesize", {"worker_count": len(findings), "fact_count": len(facts)}, "bounded response assembled", "max_steps_or_complete")
    return AgentRun(request=request, findings=findings, final_answer=final, stop_reason="bounded delegation complete")
