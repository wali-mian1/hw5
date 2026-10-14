"""Customer Service agent: drafts customer-facing messages without sending them."""

from pydantic_ai import Agent

from .models import AgentDeps, AgentResult
from .runtime import build_model, load_prompt


customer_service_agent = Agent(
    build_model(),
    deps_type=AgentDeps,
    output_type=AgentResult,
    instructions=load_prompt("customer_service"),
)
