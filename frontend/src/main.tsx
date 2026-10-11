import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://localhost:8000";
type Ticket = { ticket_id:string; title:string; customer_message:string; status:"open"|"resolved" };
type Finding = { agent:string; status:string; answer:string; facts:{name:string;price?:number}[] };
type Activity = { id:number; ticket_id:string; agent:string; statement:string; tools_json:string; created_at:string };

function App(){
  const [tickets,setTickets]=useState<Ticket[]>([]); const [selected,setSelected]=useState("101");
  const [findings,setFindings]=useState<Finding[]>([]); const [activity,setActivity]=useState<Activity[]>([]);
  const [balance,setBalance]=useState(0); const [running,setRunning]=useState(false); const [message,setMessage]=useState("");
  const load=async()=>{const [t,b,a]=await Promise.all([fetch(`${API}/tickets`),fetch(`${API}/cash/checking`),fetch(`${API}/activity`)]);setTickets(await t.json());setBalance((await b.json()).balance);setActivity(await a.json())};
  useEffect(()=>{load()},[]);
  const run=async()=>{setRunning(true);setMessage("");setFindings([]);try{const r=await fetch(`${API}/tickets/${selected}/run`,{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});const data=await r.json();if(!r.ok)throw Error(data.detail);setFindings(data.findings);setMessage(data.final_answer);await load()}catch(e){setMessage(e instanceof Error?e.message:"Run failed")}finally{setRunning(false)}};
  const approve=async()=>{const r=await fetch(`${API}/payments/${selected}/approve`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({human_approved:true})});const data=await r.json();setMessage(r.ok?`Payment approved: $${data.amount.toFixed(2)} moved by human approval.`:(data.detail||"Payment failed"));await load()};
  const ticket=tickets.find(t=>t.ticket_id===selected);
  return <div className="app"><header><div><span className="kicker">CAMPUS CUSTOMS · OPERATIONS</span><h1>Agent desk<span>.</span></h1><p>One calm control room for every customer question.</p></div><div className="balance"><small>CHECKING BALANCE</small><strong>${balance.toFixed(2)}</strong><em>Human approvals only</em></div></header><main><section className="tickets"><div className="section-title"><span>01</span><h2>Open desk tickets</h2></div>{tickets.map(t=><button className={`ticket ${selected===t.ticket_id?"chosen":""}`} onClick={()=>{setSelected(t.ticket_id);setFindings([])}} key={t.ticket_id}><span className="number">{t.ticket_id}</span><span><b>{t.title}</b><small>{t.customer_message}</small></span><i className={t.status}>{t.status}</i></button>)}</section><section className="workspace"><div className="section-title"><span>02</span><h2>{ticket?.title||"Select a ticket"}</h2></div><div className="prompt">“{ticket?.customer_message}”</div><button className="run" disabled={running||!ticket} onClick={run}>{running?<><span className="spinner"/>Agents are working…</>:"Run agent team →"}</button>{message&&<div className="summary"><small>TEAM SUMMARY</small><p>{message}</p></div>}<div className="agents">{["customer_service","inventory","accounting","facilities","boss"].map((name,i)=>{const f=findings.find(x=>x.agent===name);return <div className={`agent ${f?"done":running&&i<4?"live":""}`} key={name}><span className="dot"/><b>{name.replace("_"," ")}</b><small>{f?f.answer:running&&i<4?"Reviewing the request…":"Standing by"}</small>{f?.facts?.length?<em>{f.facts.map(x=>x.name).join(" · ")}</em>:null}</div>})}</div></section><aside><div className="section-title"><span>03</span><h2>Human controls</h2></div><p>Agents prepare the bill; only your click can move money.</p><button className="approve" onClick={approve}>{ticket?.ticket_id==="102"?"Approve $2,400 rent payment":ticket?.ticket_id==="101"?"Approve $840 reprint invoice":"No payment prepared"}</button><div className="activity"><h3>Recent activity</h3>{activity.slice(0,7).map(a=><div className="event" key={a.id}><b>{a.agent}</b><span>{a.statement}</span><small>{a.tools_json}</small></div>)}</div></aside></main></div>
}
createRoot(document.getElementById("root")!).render(<App/>);
