"""Boss agent: routes tickets, coordinates specialists, and makes final recommendations."""

from pydantic_ai import Agent

from .models import AgentDeps, AgentResult
from .runtime import build_model, load_prompt


boss_agent = Agent(
    build_model(),
    deps_type=AgentDeps,
    output_type=AgentResult,
    instructions=load_prompt("boss"),
)
