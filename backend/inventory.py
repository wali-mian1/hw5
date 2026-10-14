"""Inventory agent: evaluates stock, shortages, and replenishment facts."""

from pydantic_ai import Agent

from .models import AgentDeps, AgentResult
from .runtime import build_model, load_prompt


inventory_agent = Agent(
    build_model(),
    deps_type=AgentDeps,
    output_type=AgentResult,
    instructions=load_prompt("inventory"),
)
