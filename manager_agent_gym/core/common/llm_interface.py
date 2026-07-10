"""
Centralized LLM interface using Instructor for structured outputs.
"""

from typing import TypeVar, Type, Any
import os
from pydantic import BaseModel
from .logging import logger
from .model_provider import (
    build_litellm_model_id,
    instructor_mode_for_model,
)

__all__ = [
    "LLMInferenceTruncationError",
    "build_litellm_model_id",
    "generate_structured_response",
]

T = TypeVar("T", bound=BaseModel)


class LLMInferenceTruncationError(Exception):
    """Raised when the LLM provider indicates a truncation/content block.

    Carries provider and message context for better logging and graceful fallbacks.
    """

    def __init__(
        self,
        message: str,
        *,
        refusal_text: str | None = None,
        model: str | None = None,
        response_id: str | None = None,
        finish_reason: str | None = None,
        message_content_preview: str | None = None,
        provider_fields: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.refusal_text = refusal_text
        self.model = model
        self.response_id = response_id
        self.finish_reason = finish_reason
        self.provider_fields = provider_fields or {}

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        base = super().__str__()
        details: list[str] = []
        if self.model:
            details.append(f"model={self.model}")
        if self.finish_reason:
            details.append(f"finish_reason={self.finish_reason}")
        if self.response_id:
            details.append(f"response_id={self.response_id}")
        if self.refusal_text:
            # Trim to avoid log spam
            trimmed = (
                self.refusal_text
                if len(self.refusal_text) <= 2048
                else self.refusal_text[:2048] + "…"
            )
            details.append(f"refusal={trimmed}")

        return base + (" [" + ", ".join(details) + "]" if details else "")


_client_cache: dict[Any, Any] = {}


def _get_openai_client(mode: Any = None):
    """Get configured OpenAI async client patched by Instructor, cached by mode.

    Lazy-imports provider SDKs so they are optional until actually used.
    """
    if mode in _client_cache:
        return _client_cache[mode]

    try:
        from openai import AsyncOpenAI  # type: ignore
    except Exception as e:  # pragma: no cover - import guard
        raise ImportError(
            "OpenAI SDK is not installed. Install with `uv sync --group openai`."
        ) from e

    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        timeout=300.0,
    )

    try:
        import instructor  # type: ignore
        if mode is not None:
            instructor.patch(client, mode=mode)
        else:
            instructor.patch(client)  # type: ignore[attr-defined]
    except Exception:
        pass

    _client_cache[mode] = client
    return client


# Note: Manual prompt truncation and custom retry loops have been removed.
# Instructor handles validation and retry semantics internally.


async def generate_structured_response(
    system_prompt: str,
    user_prompt: str | None,
    response_type: Type[T],
    seed: int,
    model: str = "gpt-4o",
    temperature: float = 1,
    max_completion_tokens: int = 0,
    max_retries: int = 0,
    retry_delay_seconds: float = 0.5,
) -> T:
    """
    Generate a structured response via Instructor with Pydantic validation and provider-agnostic handling.

    Args:
        system_prompt: System prompt for the LLM
        user_prompt: User prompt for the LLM
        response_type: Pydantic model class for response validation
        seed: Random seed for reproducible outputs
        model: The OpenAI model to use for generation (must support structured outputs)
        temperature: Temperature for generation (0-2)
        max_completion_tokens: Maximum tokens to generate
        max_retries: Number of retry attempts on failure
        retry_delay_seconds: Base delay between retries (exponential backoff)

    Returns:
        Instance of response_type populated with LLM response

    Raises:
        LLMInferenceTruncationError: If no valid response is received from LLM
        ValueError: If model is not supported for structured outputs
    """
    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    client = _get_openai_client(mode=instructor_mode_for_model(model))

    try:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "response_model": response_type,
            "temperature": temperature,
            "seed": seed,
        }
        # Always pass an explicit output cap: some OpenRouter providers apply very
        # low default output limits, silently truncating structured responses.
        if not max_completion_tokens or max_completion_tokens <= 0:
            from ...config import settings

            max_completion_tokens = settings.LLM_DEFAULT_MAX_COMPLETION_TOKENS
        kwargs["max_tokens"] = max_completion_tokens

        # Delegate validation and retries to Instructor (patched method not typed)
        create_fn: Any = client.chat.completions.create
        result: T = await create_fn(
            max_retries=max_retries,
            **kwargs,
        )
        return result

    except Exception as e:
        error = LLMInferenceTruncationError(
            f"LLM request failed for {response_type.__name__}: {str(e)}",
            model=model,
            provider_fields={
                "seed": seed,
                "max_completion_tokens": max_completion_tokens,
                "temperature": temperature,
                "messages": messages,
                "response_type": response_type,
                "original_error": str(e),
                "error_type": type(e).__name__,
            },
        )
        logger.error(f"LLM request failed for {response_type.__name__}: {error}")
        raise error
