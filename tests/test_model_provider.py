import pytest

from manager_agent_gym.core.common.model_provider import (
    OPENROUTER_BASE_URL,
    build_litellm_model_id,
    resolve_native_route,
)


class TestBuildLitellmModelId:
    def test_full_routes_pass_through(self) -> None:
        assert (
            build_litellm_model_id("openrouter/deepseek/deepseek-v4-flash")
            == "openrouter/deepseek/deepseek-v4-flash"
        )
        assert build_litellm_model_id("openai/gpt-4o-mini") == "openai/gpt-4o-mini"
        assert (
            build_litellm_model_id("anthropic/claude-3-7-sonnet")
            == "anthropic/claude-3-7-sonnet"
        )
        assert build_litellm_model_id("bedrock/foo") == "bedrock/foo"

    def test_bare_names_use_upstream_heuristics(self) -> None:
        assert build_litellm_model_id("gpt-4o") == "openai/gpt-4o"
        assert build_litellm_model_id("o3") == "openai/o3"
        assert build_litellm_model_id("claude-3-7-sonnet") == "anthropic/claude-3-7-sonnet"
        assert build_litellm_model_id("gemini-2.0-flash") == "google/gemini-2.0-flash"
        assert build_litellm_model_id("eu.anthropic.claude") == "eu.anthropic.claude"


class TestResolveNativeRoute:
    def test_openrouter_non_openai_uses_md_json(self) -> None:
        import instructor

        route = resolve_native_route("openrouter/deepseek/deepseek-v4-flash")
        assert route.base_url == OPENROUTER_BASE_URL
        assert route.wire_model == "deepseek/deepseek-v4-flash"
        assert route.mode is instructor.Mode.MD_JSON

    def test_openrouter_openai_uses_tools(self) -> None:
        import instructor

        route = resolve_native_route("openrouter/openai/gpt-4o-mini")
        assert route.base_url == OPENROUTER_BASE_URL
        assert route.wire_model == "openai/gpt-4o-mini"
        assert route.mode is instructor.Mode.TOOLS

    def test_openai_native_strips_prefix(self) -> None:
        import instructor

        route = resolve_native_route("openai/gpt-4o-mini")
        assert route.base_url is None
        assert route.wire_model == "gpt-4o-mini"
        assert route.mode is instructor.Mode.TOOLS

    def test_bare_name_passes_through(self) -> None:
        import instructor

        route = resolve_native_route("gpt-4o")
        assert route.base_url is None
        assert route.wire_model == "gpt-4o"
        assert route.mode is instructor.Mode.TOOLS

    def test_openrouter_key_preferred(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test")
        route = resolve_native_route("openrouter/deepseek/deepseek-v4-flash")
        assert route.api_key == "sk-or-test"
        assert resolve_native_route("openai/gpt-4o").api_key == "sk-openai-test"

    def test_non_openai_compatible_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="openrouter/anthropic/claude-3-7-sonnet"):
            resolve_native_route("anthropic/claude-3-7-sonnet")
