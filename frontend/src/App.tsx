import { useCallback, useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

type Ticket = {
  id: number;
  type: string;
  requester: string;
  subject: string;
  sku?: string | null;
  size?: string | null;
  qty?: number | null;
  lease_id?: number | null;
  invoice_id?: number | null;
  status: string;
  notes?: string | null;
  created_at: string;
};

type Event = {
  timestamp: string;
  event: string;
  agent?: string;
  tool?: string;
  status?: string;
  result?: { summary?: string; proposed_actions?: string[] };
};

const ticketAccent: Record<number, string> = { 101: "coral", 102: "gold", 103: "ink" };

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedId, setSelectedId] = useState(101);
  const [resolved, setResolved] = useState<Set<number>>(new Set());
  const [events, setEvents] = useState<Event[]>([]);
  const [cash, setCash] = useState<{ balance: number; date: string } | null>(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [approval, setApproval] = useState({ kind: "purchase", amount: "", refId: "", approvedBy: "Manager" });

  const selectedTicket = tickets.find((ticket) => ticket.id === selectedId);
  const openCount = tickets.filter((ticket) => !resolved.has(ticket.id) && ticket.status !== "resolved").length;

  const loadDashboard = useCallback(async () => {
    try {
      const [ticketResponse, cashResponse, eventResponse] = await Promise.all([
        fetch(`${API_URL}/tickets`),
        fetch(`${API_URL}/cash`),
        fetch(`${API_URL}/events?limit=40`),
      ]);
      if (!ticketResponse.ok || !cashResponse.ok || !eventResponse.ok) throw new Error("Backend returned an error");
      const ticketData = await ticketResponse.json();
      setTickets(ticketData.tickets || []);
      setCash(await cashResponse.json());
      setEvents((await eventResponse.json()).events || []);
      setError("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not reach the backend");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
    const timer = window.setInterval(() => void loadDashboard(), 3000);
    return () => window.clearInterval(timer);
  }, [loadDashboard]);

  const runSelectedTicket = async () => {
    if (!selectedTicket || running) return;
    setRunning(true);
    setNotice(`Boss is opening ticket ${selectedTicket.id}…`);
    setError("");
    try {
      const response = await fetch(`${API_URL}/tickets/${selectedTicket.id}/run`, { method: "POST" });
      if (!response.ok) throw new Error("The agent run could not be started");
      const data = await response.json();
      const resultStatus = data.result?.status;
      if (resultStatus === "completed" || data.ticket?.status === "resolved") {
        setResolved((current) => new Set(current).add(selectedTicket.id));
        setNotice(`Ticket ${selectedTicket.id} resolved — review the trail below.`);
      } else {
        setNotice(`Ticket ${selectedTicket.id} needs human review and remains open — review the trail below.`);
      }
      await loadDashboard();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Agent run failed");
      setNotice("");
    } finally {
      setRunning(false);
    }
  };

  const approve = async () => {
    if (!approval.amount || !approval.approvedBy) return;
    try {
      const response = await fetch(`${API_URL}/approve/${approval.kind === "purchase" ? "purchase" : "payment"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kind: approval.kind,
          amount: Number(approval.amount),
          ref_id: approval.refId ? Number(approval.refId) : null,
          account: "checking",
          approved_by: approval.approvedBy,
        }),
      });
      const data = await response.json();
      if (!response.ok || data.approved === false) throw new Error(data.detail || data.reason || "Approval failed");
      setNotice(`Approved ${approval.kind} for $${Number(approval.amount).toFixed(2)}.`);
      setApproval((current) => ({ ...current, amount: "", refId: "" }));
      await loadDashboard();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Approval failed");
    }
  };

  const visibleEvents = useMemo(() => [...events].reverse().slice(0, 14), [events]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup"><span className="brand-mark">CC</span><div><span className="eyebrow">Campus Customs</span><h1>Operations desk</h1></div></div>
        <div className="connection"><span className="pulse" /> <span>{error ? "Backend offline" : "Live command center"}</span><small>localhost:8000</small></div>
      </header>

      <main>
        <section className="hero-row">
          <div><p className="eyebrow">Tuesday · August 31, 2026</p><h2>Make the next right move.</h2><p className="hero-copy">A quiet view of the shop’s open work — with the whole agent team one decision away.</p></div>
          <div className="hero-stamp"><span>SHOP STATUS</span><strong>{running ? "Agents in motion" : "Ready for review"}</strong><i>01</i></div>
        </section>

        {error && <div className="alert error">{error} <button onClick={() => void loadDashboard()}>Retry</button></div>}
        {notice && <div className="alert notice">{notice}</div>}

        <section className="metrics">
          <div className="metric"><span>Queue</span><strong>{loading ? "—" : `${openCount} open`}</strong><small>tickets waiting</small></div>
          <div className="metric"><span>Resolved this shift</span><strong>{resolved.size}</strong><small>local desk runs</small></div>
          <div className="metric cash"><span>Checking balance</span><strong>{cash ? `$${cash.balance.toLocaleString("en-US", { minimumFractionDigits: 2 })}` : "—"}</strong><small>{cash ? `as of ${cash.date}` : "loading from MCP"}</small></div>
          <div className="metric signal"><span>Agent signal</span><strong>{running ? "Working" : "Standing by"}</strong><small>{events.length} audit events visible</small></div>
        </section>

        <section className="workspace">
          <div className="tickets-column">
            <div className="section-heading"><div><p className="eyebrow">The queue</p><h3>Open tickets</h3></div><span className="count">{tickets.length} total</span></div>
            <div className="ticket-list">
              {tickets.map((ticket) => {
                const isResolved = resolved.has(ticket.id) || ticket.status === "resolved";
                return <button className={`ticket-card ${selectedId === ticket.id ? "selected" : ""} ${ticketAccent[ticket.id] || "ink"}`} key={ticket.id} onClick={() => setSelectedId(ticket.id)}>
                  <span className="ticket-number">#{ticket.id}</span><span className={`status ${isResolved ? "done" : "open"}`}>{isResolved ? "Resolved" : "Open"}</span>
                  <strong>{ticket.subject}</strong><span className="requester">{ticket.requester}</span><span className="ticket-arrow">↗</span>
                </button>;
              })}
            </div>
            <div className="approval-card"><div><p className="eyebrow">Human gate</p><h3>Approve a cash action</h3><p>Agents can prepare a payment. Only you can release it.</p></div><div className="approval-form"><select value={approval.kind} onChange={(event) => setApproval({ ...approval, kind: event.target.value })}><option value="purchase">Purchase</option><option value="invoice">Invoice payment</option><option value="rent">Rent</option></select><input aria-label="Amount" placeholder="Amount" value={approval.amount} onChange={(event) => setApproval({ ...approval, amount: event.target.value })} inputMode="decimal" /><input aria-label="Reference ID" placeholder="Ref ID" value={approval.refId} onChange={(event) => setApproval({ ...approval, refId: event.target.value })} /><button onClick={() => void approve()}>Approve ↗</button></div></div>
          </div>

          <div className="detail-column">
            {selectedTicket && <div className={`ticket-detail ${ticketAccent[selectedTicket.id] || "ink"}`}>
              <div className="detail-top"><div><span className="eyebrow">Selected ticket · {selectedTicket.type.replaceAll("_", " ")}</span><h2>{selectedTicket.subject}</h2><p>{selectedTicket.notes}</p></div><span className="big-id">{selectedTicket.id}</span></div>
              <div className="facts"><span><small>REQUESTER</small><b>{selectedTicket.requester}</b></span><span><small>REQUEST</small><b>{selectedTicket.qty || 1} {selectedTicket.sku || "Lease notice"}{selectedTicket.size ? ` · ${selectedTicket.size}` : ""}</b></span><span><small>CREATED</small><b>{new Date(selectedTicket.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</b></span></div>
              <div className="run-row"><p>Ready to route this ticket through the full team.</p><button className="run-button" disabled={running} onClick={() => void runSelectedTicket()}>{running ? <><span className="spinner" /> Team is working</> : <>Start agent team <span>→</span></>}</button></div>
            </div>}
            <div className="activity-panel"><div className="section-heading"><div><p className="eyebrow">Live trail</p><h3>What the desk is hearing</h3></div><span className="live-dot">● Live</span></div>
              <div className="event-list">{visibleEvents.length ? visibleEvents.map((event, index) => <div className="event" key={`${event.timestamp}-${index}`}><span className="event-line" /><div><div className="event-meta"><b>{event.agent || "SYSTEM"}</b><time>{new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time></div><p>{event.event === "mcp_tool_call" ? <>queried <code>{event.tool}</code></> : event.event === "agent_result" ? event.result?.summary || `finished with status ${event.status}` : event.event.replaceAll("_", " ")}</p></div></div>) : <div className="empty-state"><span>◌</span><p>Run a ticket to see the team’s trail here.</p></div>}</div>
            </div>
          </div>
        </section>
      </main>
      <footer><span>Campus Customs / internal use</span><span>Facts supplied by MCP · actions require human approval</span></footer>
    </div>
  );
}

export default App;
