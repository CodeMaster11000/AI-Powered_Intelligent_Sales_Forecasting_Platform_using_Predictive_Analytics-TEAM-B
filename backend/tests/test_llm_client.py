import pytest
from backend.ai_agents.llm_client import LLMClient


def test_llm_client_initialization():
    client = LLMClient()
    providers = client.get_available_providers()
    assert "gemini" in providers
    assert "openai" in providers
    assert "grok" in providers
    assert "ollama" in providers
    assert "preferred_provider" in providers


def test_provider_order_resolution():
    client = LLMClient()
    # Default order
    default_order = client._determine_provider_order("auto")
    assert default_order == ["gemini", "openai", "grok", "ollama"]

    # Explicit preference
    grok_order = client._determine_provider_order("grok")
    assert grok_order[0] == "grok"

    ollama_order = client._determine_provider_order("ollama")
    assert ollama_order[0] == "ollama"

    openai_order = client._determine_provider_order("openai")
    assert openai_order[0] == "openai"


def test_json_parser_clean():
    client = LLMClient()
    # Standard clean JSON
    res = client._parse_json('{"key": "value", "score": 90}')
    assert res == {"key": "value", "score": 90}


def test_json_parser_markdown_fence():
    client = LLMClient()
    # Wrapped in markdown code fence
    raw = """```json
{
  "status": "success",
  "items": [1, 2, 3]
}
```"""
    res = client._parse_json(raw)
    assert res == {"status": "success", "items": [1, 2, 3]}


def test_json_parser_with_surrounding_text():
    client = LLMClient()
    # Raw output containing preamble text
    raw = "Here is the response requested:\n{\"decision\": \"approved\"}\nHope this helps!"
    res = client._parse_json(raw)
    assert res == {"decision": "approved"}


def test_offline_fallback_returns_none():
    client = LLMClient()
    # When all API keys are unconfigured and Ollama is offline
    client.gemini_available = False
    client.openai_available = False
    client.grok_available = False
    client.ollama_available = False

    result = client.generate_json("System prompt", "User prompt")
    assert result is None

    text_result = client.generate_text("System prompt", "User prompt")
    assert text_result is None
