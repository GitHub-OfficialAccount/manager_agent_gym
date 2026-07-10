"""
Provider routing policy for all LLM calls.

Model names are full LiteLLM-style routes; the name alone determines where
traffic goes — there is no global endpoint state:

- ``openrouter/<provider>/<model>`` → via OpenRouter (any role)
- ``openai/<model>``                → OpenAI native
- ``anthropic/<model>``, ``google/<model>``, ... → that provider via LiteLLM
  (workers/human-mocks/stakeholder only; not supported for manager/judge)
- bare names (``gpt-4o``, ``claude-3-7-sonnet``) → upstream prefix heuristics,
  kept for backward compatibility

Two call paths consume these routes:

- LiteLLM path (AI workers, human mocks, stakeholder): LiteLLM understands the
  full route directly; only bare names need a provider prefix added.
- Native path (manager, LLM judges): an OpenAI-compatible client; the route
  prefix determines base URL, API key, the model id sent over the wire, and
  the Instructor mode.
"""

import os
from dataclasses import dataclass
from typing import Any, Literal

ModelRole = Literal["manager", "worker", "stakeholder", "judge"]

_OPENROUTER_PREFIX = "openrouter/"
_OPENAI_PREFIX = "openai/"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_model_for_role(role: ModelRole) -> str:
    """Resolve the default model route for a role from Settings (.env)."""
    from ...config import settings

    return {
        "manager": settings.MANAGER_MODEL_NAME,
        "worker": settings.WORKER_MODEL_NAME,
        "stakeholder": settings.STAKEHOLDER_MODEL_NAME,
        "judge": settings.JUDGE_MODEL_NAME,
    }[role]


def build_litellm_model_id(model_id: str) -> str:
    """Build the LiteLLM model ID for the worker/human-mock/stakeholder path.

    Provider-prefixed names are already full LiteLLM routes and pass through
    unchanged (``openrouter/deepseek/x``, ``openai/gpt-4o-mini``,
    ``anthropic/claude-...``, ``bedrock/...``). Bare names fall back to
    upstream routing heuristics.
    """
    if "/" in model_id:
        return model_id

    # Native provider routing for bare names (upstream behavior).
    if model_id.startswith(("gpt-", "o")):
        return f"openai/{model_id}"
    elif model_id.startswith("claude-"):
        return f"anthropic/{model_id}"
    elif model_id.startswith("gemini-"):
        return f"google/{model_id}"
    else:
        return model_id


@dataclass(frozen=True)
class NativeRoute:
    """Where and how the native (OpenAI-compatible) client reaches a model."""

    base_url: str | None  # None = OpenAI default endpoint
    api_key: str | None
    wire_model: str  # model id sent over the wire
    mode: Any  # instructor.Mode


def resolve_native_route(model: str) -> NativeRoute:
    """Resolve a model route for the manager/judge structured-output path.

    Several non-OpenAI providers behind OpenRouter mis-handle OpenAI tool-call
    grammars, so those models use JSON-in-markdown extraction (MD_JSON)
    instead of tool calling.
    """
    import instructor

    if model.startswith(_OPENROUTER_PREFIX):
        wire_model = model[len(_OPENROUTER_PREFIX) :]
        is_openai_model = "gpt-" in wire_model or wire_model.startswith(_OPENAI_PREFIX)
        return NativeRoute(
            base_url=OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
            wire_model=wire_model,
            mode=instructor.Mode.TOOLS if is_openai_model else instructor.Mode.MD_JSON,
        )
    if model.startswith(_OPENAI_PREFIX):
        return NativeRoute(
            base_url=None,
            api_key=os.getenv("OPENAI_API_KEY"),
            wire_model=model[len(_OPENAI_PREFIX) :],
            mode=instructor.Mode.TOOLS,
        )
    if "/" in model:
        raise ValueError(
            f"Model '{model}' routes to a non-OpenAI-compatible provider; the "
            "manager/judge path only supports 'openai/...', 'openrouter/...', "
            f"or bare OpenAI names. Use 'openrouter/{model}' to reach it via "
            "OpenRouter."
        )
    # Bare name: send as-is to the default OpenAI endpoint (upstream behavior).
    return NativeRoute(
        base_url=None,
        api_key=os.getenv("OPENAI_API_KEY"),
        wire_model=model,
        mode=instructor.Mode.TOOLS,
    )


def disable_agents_tracing_if_proxied() -> None:
    """Disable OpenAI Agents SDK tracing when traffic is routed off OpenAI.

    The Agents SDK uploads traces to platform.openai.com with OPENAI_API_KEY;
    when that key is an OpenRouter key (or roles route through OpenRouter),
    the uploads fail with 401 spam.
    """
    proxied = os.getenv("OPENAI_API_KEY", "").startswith("sk-or-") or any(
        get_model_for_role(role).startswith(_OPENROUTER_PREFIX)
        for role in ("manager", "worker", "stakeholder", "judge")
    )
    if not proxied:
        return
    os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")
    try:
        from agents import set_tracing_disabled

        set_tracing_disabled(True)
    except Exception:
        pass
