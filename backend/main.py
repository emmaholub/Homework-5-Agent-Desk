from __future__ import annotations
import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mcp_server.server import get_financial_context, get_ticket, check_inventory_and_price
from backend.boss_agent import run as run_agent_team
from backend.models import AgentRequest

DB = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
app = FastAPI(title="Campus Customs Operations")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5176", "http://127.0.0.1:5176",
    ],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
)

def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def ts(): return datetime.now(timezone.utc).isoformat()
def ticket_view(row):
    return {"ticket_id":str(row["id"]),"title":row["subject"],"customer_message":row["notes"],"status":row["status"],"type":row["type"],"requester":row["requester"]}

class Approval(BaseModel):
    human_approved: bool

@app.get("/tickets")
def tickets():
    with conn() as c: return [ticket_view(r) for r in c.execute("SELECT * FROM tickets ORDER BY id")]

@app.post("/tickets/{ticket_id}/run")
def run_ticket(ticket_id: int):
    ticket=get_ticket(ticket_id)
    if not ticket: raise HTTPException(404,"Unknown ticket")
    agent_run = run_agent_team(AgentRequest(ticket_id=ticket_id, message=ticket["notes"], product_id=ticket["sku"]))
    findings = [finding.model_dump() for finding in agent_run.findings]
    tools = sorted({event.action.removeprefix("mcp.") for event in []})
    if ticket["type"] == "customer_order": tools = ["get_ticket", "check_inventory_and_price"]
    elif ticket["type"] == "rent_notice": tools = ["get_ticket", "get_financial_context"]
    else: tools = ["get_ticket", "check_inventory_and_price"]
    with conn() as c:
        c.execute("UPDATE tickets SET status='resolved',notes=notes||' [resolved]' WHERE id=?",(ticket_id,))
        for f in findings: c.execute("INSERT INTO desk(date_today,notes) VALUES(?,?)",(ts(),json.dumps({"ticket_id":ticket_id,"agent":f["agent"],"answer":f["answer"],"tools":tools})))
    return {"ticket_id":str(ticket_id),"final_answer":agent_run.final_answer,"findings":findings,"tools":tools,"stop_reason":agent_run.stop_reason}

@app.get("/activity")
def activity(limit:int=25):
    with conn() as c:
        rows=c.execute("SELECT rowid AS id,date_today AS created_at,notes FROM desk ORDER BY rowid DESC LIMIT ?",(max(1,min(limit,100)),)).fetchall()
    output=[]
    for row in rows:
        item=dict(row)
        try:
            note=json.loads(item.pop("notes"))
        except (TypeError, json.JSONDecodeError):
            note={}
        item.update({"agent":note.get("agent","system"),"statement":note.get("answer",note.get("result","")),"tools_json":json.dumps(note.get("tools",[]))})
        output.append(item)
    return output

@app.post("/payments/{ticket_id}/approve")
def approve(ticket_id:int, payment:Approval):
    if not payment.human_approved: raise HTTPException(400,"Human approval is required")
    amounts = {101: (840.0, "Overdue invoice 501 reprint of CC-TEE-WHITE size S"), 102: (2400.0, "Chapel Street shop rent")}
    if ticket_id not in amounts:
        raise HTTPException(409, "No payment is prepared for this ticket")
    amount, description = amounts[ticket_id]
    with conn() as c:
        account=c.execute("SELECT balance FROM cash_accounts WHERE name='checking'").fetchone()
        if not account or account["balance"]<amount: raise HTTPException(409,"Insufficient checking balance")
        c.execute("UPDATE cash_accounts SET balance=balance-?,date=? WHERE name='checking'",(amount,ts()))
        cur=c.execute("INSERT INTO payments(kind,ref_id,amount,account,paid_at,approved_by) VALUES('ticket',?,?,?,?,?)",(ticket_id,amount,'checking',ts(),'human'))
        c.execute("INSERT INTO desk(date_today,notes) VALUES(?,?)",(ts(),json.dumps({"ticket_id":ticket_id,"agent":"human","answer":f"Approved {description} for ${amount:.2f}","tools":[]})))
    return {"payment_id":cur.lastrowid,"status":"approved","amount":amount,"moved_money":True}

@app.get("/cash/checking")
def cash():
    with conn() as c: return dict(c.execute("SELECT name AS account_name,balance,date FROM cash_accounts WHERE name='checking'").fetchone())

@app.post("/reset")
def reset():
    with conn() as c:
        c.execute("UPDATE tickets SET status='open', notes=replace(notes, ' [resolved]', '')")
        c.execute("DELETE FROM payments"); c.execute("DELETE FROM desk")
        c.execute("UPDATE cash_accounts SET balance=3400.0,date='2026-08-31' WHERE name='checking'")
    return {"status":"reset","starting_balance":3400.0}
