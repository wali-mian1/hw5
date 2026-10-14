"""Fully connected PydanticAI team with MCP-only shop facts and audit logging."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic_ai import Agent, RunContext, UsageLimits

from .accounting import accounting_agent
from .audit import AuditTrail
from .boss import boss_agent
from .customer_service import customer_service_agent
from .facilities import facilities_agent
from .inventory import inventory_agent
from .mcp_client import MCPShopTools
from .models import AgentDeps, AgentResult
from .runtime import MAX_DELEGATION_DEPTH, MAX_OUTPUT_TOKENS


AGENTS: dict[str, Agent[AgentDeps, AgentResult]] = {
    "boss": boss_agent,
    "inventory": inventory_agent,
    "accounting": accounting_agent,
    "facilities": facilities_agent,
    "customer_service": customer_service_agent,
}


def _add_mcp_tools(agent: Agent[AgentDeps, AgentResult]) -> None:
    async def read_ticket(ctx: RunContext[AgentDeps], ticket_id: int) -> dict[str, Any]:
        return await ctx.deps.shop.get_ticket(ticket_id)

    async def list_open_tickets(ctx: RunContext[AgentDeps]) -> dict[str, Any]:
        return await ctx.deps.shop.get_open_tickets()

    async def check_inventory(ctx: RunContext[AgentDeps], sku: str, size: str) -> dict[str, Any]:
        return await ctx.deps.shop.check_inventory(sku, size)

    async def get_product_pricing(ctx: RunContext[AgentDeps], sku: str) -> dict[str, Any]:
        return await ctx.deps.shop.get_pricing(sku)

    async def get_invoice_details(ctx: RunContext[AgentDeps], invoice_id: int) -> dict[str, Any]:
        return await ctx.deps.shop.get_invoice(invoice_id)

    async def get_lease_details(ctx: RunContext[AgentDeps], lease_id: int) -> dict[str, Any]:
        return await ctx.deps.shop.get_lease(lease_id)

    async def get_cash_balance(ctx: RunContext[AgentDeps], account: str) -> dict[str, Any]:
        return await ctx.deps.shop.get_cash_balance(account)

    for function in (
        read_ticket,
        list_open_tickets,
        check_inventory,
        get_product_pricing,
        get_invoice_details,
        get_lease_details,
        get_cash_balance,
    ):
        agent.tool(function)


def _add_delegation_tools(agent: Agent[AgentDeps, AgentResult], role: str) -> None:
    def make_delegate(target: str):
        async def delegate(ctx: RunContext[AgentDeps], request: str) -> AgentResult:
            return await ctx.deps.team.run(target, request, ctx.deps)

        delegate.__name__ = f"delegate_to_{target}"
        delegate.__doc__ = f"Delegate a focused task to the {target} agent and receive its typed result."
        return delegate

    for target in AGENTS:
        if target != role:
            agent.tool(make_delegate(target))


for _role, _agent in AGENTS.items():
    _add_mcp_tools(_agent)
    _add_delegation_tools(_agent, _role)


class AgentTeam:
    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path(__file__).resolve().parents[1]
        self.audit = AuditTrail(root / "output" / "audit_trail.json")
        self.shop = MCPShopTools(self.audit)
        self.agents = AGENTS

    async def run(
        self, role: str, request: str, parent: AgentDeps | None = None
    ) -> AgentResult:
        if role not in self.agents:
            raise ValueError(f"Unknown agent role: {role}")
        depth = 0 if parent is None else parent.depth + 1
        run_id = str(uuid4()) if parent is None else parent.run_id
        if depth > MAX_DELEGATION_DEPTH:
            return AgentResult(
                agent=role,
                status="blocked",
                summary="Delegation limit reached; a human must review the remaining work.",
                blockers=["Maximum delegation depth exceeded"],
            )
        deps = AgentDeps(
            shop=self.shop,
            audit=self.audit,
            team=self,
            run_id=run_id,
            depth=depth,
        )
        self.audit.append({
            "event": "agent_start",
            "run_id": run_id,
            "agent": role,
            "depth": depth,
            "request": request,
        })
        result = await self.agents[role].run(
            request,
            deps=deps,
            usage_limits=UsageLimits(
                request_limit=8,
                output_tokens_limit=MAX_OUTPUT_TOKENS,
            ),
            model_settings={"max_tokens": MAX_OUTPUT_TOKENS},
        )
        output = result.output
        self.audit.append({
            "event": "agent_result",
            "run_id": run_id,
            "agent": role,
            "depth": depth,
            "status": output.status,
            "result": output.model_dump(),
        })
        return output

    async def run_ticket(self, ticket_id: int) -> AgentResult:
        return await self.run(
            "boss",
            f"Coordinate a careful resolution plan for open ticket {ticket_id}. Read the ticket through MCP first.",
        )

    async def run_open_tickets(self) -> list[AgentResult]:
        tickets = await self.shop.get_open_tickets()
        results: list[AgentResult] = []
        for ticket in tickets.get("tickets", []):
            results.append(await self.run_ticket(int(ticket["id"])))
        return results


async def run_ticket(ticket_id: int) -> AgentResult:
    """Convenience entry point for one ticket; later app layers can import this."""
    return await AgentTeam().run_ticket(ticket_id)
