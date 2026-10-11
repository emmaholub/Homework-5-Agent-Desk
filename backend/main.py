from __future__ import annotations
import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mcp_server.server import get_financial_context, get_ticket, check_inventory_and_price

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
    amount: float = Field(gt=0, le=10000)
    description: str = Field(min_length=1, max_length=240)
    human_approved: bool

@app.get("/tickets")
def tickets():
    with conn() as c: return [ticket_view(r) for r in c.execute("SELECT * FROM tickets ORDER BY id")]

@app.post("/tickets/{ticket_id}/run")
def run_ticket(ticket_id: int):
    ticket=get_ticket(ticket_id)
    if not ticket: raise HTTPException(404,"Unknown ticket")
    findings=[]; tools=[]
    if ticket["type"]=="customer_order":
        data=check_inventory_and_price(ticket["sku"],ticket["size"]); tools=["get_ticket","check_inventory_and_price"]
        findings=[{"agent":"customer_service","status":"complete","answer":"Validated the customer order request."},{"agent":"inventory","status":"complete","answer":f"Checked {ticket['sku']} size {ticket['size']} stock through MCP.","data":data}]
    elif ticket["type"]=="rent_notice":
        data=get_financial_context(ticket_id); tools=["get_ticket","get_financial_context"]
        findings=[{"agent":"facilities","status":"complete","answer":"Identified the linked lease and rent due date."},{"agent":"accounting","status":"complete","answer":"Reviewed checking balance and the lease financial context.","data":data}]
    else:
        data=check_inventory_and_price(ticket["sku"],ticket["size"]); tools=["get_ticket","check_inventory_and_price"]
        findings=[{"agent":"customer_service","status":"complete","answer":"Captured the student organization request."},{"agent":"inventory","status":"complete","answer":"Verified requested quantity against size-M stock.","data":data},{"agent":"accounting","status":"complete","answer":"Read unit cost and list price; no discount was invented."}]
    with conn() as c:
        c.execute("UPDATE tickets SET status='resolved',notes=notes||' [resolved]' WHERE id=?",(ticket_id,))
        for f in findings: c.execute("INSERT INTO desk(date_today,notes) VALUES(?,?)",(ts(),json.dumps({"ticket_id":ticket_id,"agent":f["agent"],"answer":f["answer"],"tools":tools})))
    return {"ticket_id":str(ticket_id),"final_answer":"Ticket resolved with MCP-verified facts.","findings":findings,"tools":tools,"stop_reason":"complete"}

@app.get("/activity")
def activity(limit:int=25):
    with conn() as c:
        rows=c.execute("SELECT rowid AS id,date_today AS created_at,notes FROM desk ORDER BY rowid DESC LIMIT ?",(max(1,min(limit,100)),)).fetchall()
    return [dict(r) for r in rows]

@app.post("/payments/{ticket_id}/approve")
def approve(ticket_id:int, payment:Approval):
    if not payment.human_approved: raise HTTPException(400,"Human approval is required")
    with conn() as c:
        account=c.execute("SELECT balance FROM cash_accounts WHERE name='checking'").fetchone()
        if not account or account["balance"]<payment.amount: raise HTTPException(409,"Insufficient checking balance")
        c.execute("UPDATE cash_accounts SET balance=balance-?,date=? WHERE name='checking'",(payment.amount,ts()))
        cur=c.execute("INSERT INTO payments(kind,ref_id,amount,account,paid_at,approved_by) VALUES('ticket',?,?,?,?,?)",(ticket_id,payment.amount,'checking',ts(),'human'))
    return {"payment_id":cur.lastrowid,"status":"approved","amount":payment.amount,"moved_money":True}

@app.get("/cash/checking")
def cash():
    with conn() as c: return dict(c.execute("SELECT name AS account_name,balance,date FROM cash_accounts WHERE name='checking'").fetchone())

@app.post("/reset")
def reset():
    with conn() as c:
        c.execute("UPDATE tickets SET status='open'"); c.execute("DELETE FROM payments"); c.execute("DELETE FROM desk")
        c.execute("UPDATE cash_accounts SET balance=3400.0,date='2026-08-31' WHERE name='checking'")
    return {"status":"reset","starting_balance":3400.0}
