from __future__ import annotations

import os
from pathlib import Path

from pydantic_ai import Agent


PROMPTS = Path(__file__).parent / "prompts"


def make_agent(filename: str, result_type: type):
    """Create a PydanticAI agent using Portkey's OpenAI-compatible endpoint."""
    prompt = (PROMPTS / filename).read_text(encoding="utf-8")
    key = os.environ.get("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is required")
    # Portkey is the only model gateway and gpt-6-luna is the only approved
    # model for this homework.
    os.environ.setdefault("OPENAI_API_KEY", key)
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.portkey.ai/v1")
    return Agent("openai:gpt-6-luna", system_prompt=prompt, output_type=result_type)
