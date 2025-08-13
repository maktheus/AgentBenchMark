"""
Testes para os agents
"""

import pytest
from benchmark_service.agents.openai_adapter import OpenAIAgentAdapter, OpenAIConfig
from benchmark_service.agents.anthropic_adapter import (
    AnthropicAgentAdapter,
    AnthropicConfig,
)
from benchmark_service.agents.local_adapter import LocalAgentAdapter, LocalAgentConfig


def test_openai_adapter_info():
    """Testa informações do adapter OpenAI"""
    config = OpenAIConfig(api_key="test-key", model="gpt-4-turbo")
    adapter = OpenAIAgentAdapter(config)

    info = adapter.get_info()
    assert info["name"] == "openai"
    assert info["model"] == "gpt-4-turbo"
    assert "text-generation" in info["capabilities"]


def test_anthropic_adapter_info():
    """Testa informações do adapter Anthropic"""
    config = AnthropicConfig(api_key="test-key", model="claude-3-opus-20240229")
    adapter = AnthropicAgentAdapter(config)

    info = adapter.get_info()
    assert info["name"] == "anthropic"
    assert info["model"] == "claude-3-opus-20240229"
    assert "reasoning" in info["capabilities"]


def test_local_adapter_info():
    """Testa informações do adapter local"""
    config = LocalAgentConfig(
        endpoint="http://localhost:8001/chat", model="local-test-model"
    )
    adapter = LocalAgentAdapter(config)

    info = adapter.get_info()
    assert info["name"] == "local"
    assert info["model"] == "local-test-model"
    assert "text-generation" in info["capabilities"]
