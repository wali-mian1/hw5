"""FastAPI routes for the Campus Customs React dashboard."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.audit import AuditTrail  # noqa: E402
from backend.mcp_client import MCPShopTools  # noqa: E402
from backend.team import AgentTeam  # noqa: E402


app = FastAPI(title="Campus Customs Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audit = AuditTrail(PROJECT_ROOT / "output" / "audit_trail.json")
shop = MCPShopTools(audit)
team = AgentTeam(PROJECT_ROOT)


class ApprovalRequest(BaseModel):
    kind: str = Field(description="invoice, rent, or purchase")
    ref_id: int | None = None
    amount: float = Field(gt=0)
    account: str = "checking"
    approved_by: str = Field(min_length=1)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tickets")
async def get_tickets() -> dict[str, Any]:
    """Return all tickets and current status through MCP."""
    return await shop.call("list_tickets")


@app.post("/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int) -> dict[str, Any]:
    """Run Boss and the connected agent team for one ticket."""
    ticket = await shop.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    result = await team.run_ticket(ticket_id)
    return {"ticket": ticket, "result": result.model_dump()}


@app.get("/events")
async def get_recent_events(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    """Return recent append-only agent and MCP audit events for board refreshes."""
    if not audit.path.exists():
        return {"events": []}
    events = __import__("json").loads(audit.path.read_text())
    return {"events": events[-limit:]}


@app.post("/approve/payment")
async def approve_payment(request: ApprovalRequest) -> dict[str, Any]:
    """Apply a payment only after a human approval request reaches this route."""
    if request.kind not in {"invoice", "rent", "purchase"}:
        raise HTTPException(status_code=400, detail="Unsupported payment kind")
    return await shop.call(
        "approve_payment",
        kind=request.kind,
        ref_id=request.ref_id,
        amount=request.amount,
        account=request.account,
        approved_by=request.approved_by,
    )


@app.post("/approve/purchase")
async def approve_purchase(request: ApprovalRequest) -> dict[str, Any]:
    """Use the same guarded cash mutation for an explicitly approved purchase."""
    request.kind = "purchase"
    return await shop.call(
        "approve_payment",
        kind=request.kind,
        ref_id=request.ref_id,
        amount=request.amount,
        account=request.account,
        approved_by=request.approved_by,
    )


@app.get("/cash")
async def get_cash(account: str = "checking") -> dict[str, Any]:
    """Return the current checking balance through MCP."""
    return await shop.get_cash_balance(account)


@app.post("/reset")
async def reset_database() -> dict[str, Any]:
    """Reset the working database from the untouched original database."""
    return await shop.call("reset_database")
