"""Typed inputs and outputs shared by the Campus Customs agent team."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel, Field


class ShopTools(Protocol):
    async def call(self, tool_name: str, **arguments: Any) -> dict[str, Any]: ...


class AuditWriter(Protocol):
    def append(self, event: dict[str, Any]) -> None: ...


class AgentResult(BaseModel):
    """A compact, auditable result returned by every specialist."""

    agent: str
    status: str = Field(description="completed, needs_human, blocked, or delegated")
    summary: str
    database_facts: list[str] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    delegated_to: list[str] = Field(default_factory=list)
    human_approval_required: bool = False
    customer_message_draft: str | None = None
    blockers: list[str] = Field(default_factory=list)


@dataclass
class AgentDeps:
    """Runtime dependencies; shop facts are available only through MCPShopTools."""

    shop: ShopTools
    audit: AuditWriter
    team: Any
    run_id: str
    depth: int = 0
    delegated_to: list[str] = field(default_factory=list)
