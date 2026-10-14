"""Async MCP client used by every agent; no shop database access lives here."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPShopTools:
    """Call the authoritative FastMCP server over stdio."""

    def __init__(self, audit: Any | None = None) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.audit = audit

    async def call(self, tool_name: str, **arguments: Any) -> dict[str, Any]:
        python_path = self.project_root / ".venv" / "bin" / "python"
        server_path = self.project_root / "mcp_server" / "server.py"
        parameters = StdioServerParameters(
            command=str(python_path),
            args=[str(server_path)],
        )
        if self.audit is not None:
            self.audit.append({"event": "mcp_tool_call", "tool": tool_name, "arguments": arguments})
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
        structured = getattr(result, "structuredContent", None)
        return structured if isinstance(structured, dict) else {}

    async def get_open_tickets(self) -> dict[str, Any]:
        return await self.call("list_open_tickets")

    async def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        return await self.call("get_ticket", ticket_id=ticket_id)

    async def check_inventory(self, sku: str, size: str) -> dict[str, Any]:
        return await self.call("check_inventory", sku=sku, size=size)

    async def get_pricing(self, sku: str) -> dict[str, Any]:
        return await self.call("get_product_pricing", sku=sku)

    async def get_invoice(self, invoice_id: int) -> dict[str, Any]:
        return await self.call("get_invoice_details", invoice_id=invoice_id)

    async def get_lease(self, lease_id: int) -> dict[str, Any]:
        return await self.call("get_lease_details", lease_id=lease_id)

    async def get_cash_balance(self, account: str) -> dict[str, Any]:
        return await self.call("get_cash_balance", account=account)
