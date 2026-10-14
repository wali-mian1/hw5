"""Shared PydanticAI model and prompt-loading configuration."""

from __future__ import annotations

import os
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider


MODEL_NAME = "gpt-6-luna"
# Enough room for a typed result after MCP calls and specialist delegation,
# while still bounding every individual agent invocation.
MAX_OUTPUT_TOKENS = 2400
MAX_DELEGATION_DEPTH = 4


def _load_course_env() -> None:
    for parent in Path(__file__).resolve().parents:
        env_path = parent / ".env"
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        break


def build_model() -> OpenAIResponsesModel:
    _load_course_env()
    api_key = os.environ["PORTKEY_API_KEY"]
    provider = OpenAIProvider(
        openai_client=AsyncOpenAI(api_key=api_key, base_url="https://api.portkey.ai/v1")
    )
    return OpenAIResponsesModel(MODEL_NAME, provider=provider)


def load_prompt(agent_name: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / f"{agent_name}.md"
    return path.read_text()
