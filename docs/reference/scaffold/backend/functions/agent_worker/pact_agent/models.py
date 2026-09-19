"""Model factory. Bedrock for the deployed worker (Ship It), Ollama for the local bench (Build It)."""

from __future__ import annotations

import os

DEFAULT_ALIASES = "nova-2-lite=us.amazon.nova-2-lite-v1:0,nova-pro=us.amazon.nova-pro-v1:0"


def parse_aliases(spec: str | None = None) -> dict[str, str]:
    """'a=model-id,b=other-id' -> {'a': 'model-id', 'b': 'other-id'} (order preserved; first = default)."""
    out: dict[str, str] = {}
    for part in (spec if spec is not None else os.environ.get("AGENT_MODELS", DEFAULT_ALIASES)).split(","):
        if "=" in part:
            alias, model_id = part.split("=", 1)
            if alias.strip() and model_id.strip():
                out[alias.strip()] = model_id.strip()
    return out


def resolve(alias_or_id: str) -> tuple[str, str]:
    """Return (alias, bedrock model/profile id). Unknown aliases are treated as raw model ids."""
    aliases = parse_aliases()
    if alias_or_id in aliases:
        return alias_or_id, aliases[alias_or_id]
    return alias_or_id, alias_or_id


def build_model(backend: str, model: str, *, region: str | None = None, ollama_host: str | None = None):
    if backend == "bedrock":
        from strands.models import BedrockModel

        _, model_id = resolve(model)
        return BedrockModel(
            model_id=model_id,
            region_name=region or os.environ.get("BEDROCK_REGION", "us-east-1"),
            temperature=0.0,
            max_tokens=400,
            streaming=False,
        )
    if backend == "ollama":
        from strands.models.ollama import OllamaModel

        return OllamaModel(
            ollama_host or os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            model_id=model,
            temperature=0.0,
            max_tokens=400,
        )
    raise ValueError(f"unknown backend {backend!r} (expected bedrock|ollama)")
