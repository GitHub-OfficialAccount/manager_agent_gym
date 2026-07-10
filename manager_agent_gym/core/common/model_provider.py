"""
Provider routing policy for all LLM calls.

Single home for every decision about which model serves a role and how it is
reached: per-role default model names from Settings, OpenRouter vs. native
provider routing for the LiteLLM path (workers, human mocks, stakeholder),
Instructor mode selection for the native structured-output path (manager, LLM
judges), and the Agents SDK tracing kill-switch needed when the OpenAI client
is pointed at a non-OpenAI endpoint.

OpenRouter is enabled by configuration, not code changes: set OPENROUTER_API_KEY
(LiteLLM path) and OPENAI_BASE_URL=https://openrouter.ai/api/v1 (native path)
in .env, and use full OpenRouter slugs (e.g. "openai/gpt-4o-mini",
"anthropic/claude-3.7-sonnet") as model names. With neither set, routing falls
back to upstream behavior: bare model names routed to their native providers.
"""

import os
from typing import Any, Literal

ModelRole = Literal["manager", "worker", "stakeholder", "judge"]

_OPENROUTER_PREFIX = "openrouter/"


def get_model_for_role(role: ModelRole) -> str:
    """Resolve the default model name for a role from Settings (.env)."""
    from ...config import settings

    return {
        "manager": settings.MANAGER_MODEL_NAME,
        "worker": settings.WORKER_MODEL_NAME,
        "stakeholder": settings.STAKEHOLDER_MODEL_NAME,
        "judge": settings.JUDGE_MODEL_NAME,
    }[role]


def is_openrouter_configured() -> bool:
    """True when LLM traffic is routed through OpenRouter.

    Either signal counts: the native OpenAI client's base URL points at
    OpenRouter, or an OpenRouter key is present for the LiteLLM path.
    """
    if "openrouter.ai" in os.getenv("OPENAI_BASE_URL", ""):
        return True
    key = os.getenv("OPENROUTER_API_KEY", "")
    return bool(key) and key != "na"


def build_litellm_model_id(model_id: str) -> str:
    """Build the LiteLLM model ID for the worker/human-mock/stakeholder path.

    When OpenRouter is configured, model names are expected to be full
    OpenRouter slugs and just get the ``openrouter/`` provider prefix.
    Otherwise, fall back to upstream native routing by model-name prefix.
    """
    if model_id.startswith(_OPENROUTER_PREFIX):
        return model_id
    if is_openrouter_configured():
        return f"{_OPENROUTER_PREFIX}{model_id}"

    # Native provider routing (upstream behavior).
    if model_id.startswith(("gpt-", "o")):
        return f"openai/{model_id}"
    elif model_id.startswith("claude-"):
        return f"anthropic/{model_id}"
    elif model_id.startswith("gemini-"):
        return f"google/{model_id}"
    elif model_id.startswith(("eu.anthropic.", "eu.openai.", "eu.google.", "bedrock/")):
        return model_id
    else:
        return model_id


def instructor_mode_for_model(model: str) -> Any:
    """Pick the Instructor mode for the native-client structured-output path.

    Several non-OpenAI providers behind OpenRouter mis-handle OpenAI tool-call
    grammars, so those models use JSON-in-markdown extraction instead of tool
    calling. Returns an ``instructor.Mode`` (typed Any to keep the import lazy).
    """
    import instructor

    is_openrouter = is_openrouter_configured() or model.startswith(_OPENROUTER_PREFIX)
    is_openai_model = "gpt-" in model or model.startswith("openai/")
    if is_openrouter and not is_openai_model:
        return instructor.Mode.MD_JSON
    return instructor.Mode.TOOLS


def disable_agents_tracing_if_proxied() -> None:
    """Disable OpenAI Agents SDK tracing when using a non-OpenAI endpoint.

    The Agents SDK uploads traces to platform.openai.com with the configured
    key; behind OpenRouter that key is not an OpenAI key, causing 401 spam.
    """
    base_url = os.getenv("OPENAI_BASE_URL", "")
    if base_url in ("", "na") or "openai.com" in base_url:
        return
    os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")
    try:
        from agents import set_tracing_disabled

        set_tracing_disabled(True)
    except Exception:
        pass
