"""
Testes para o adapter local
"""

import pytest
from unittest.mock import patch, AsyncMock
from benchmark_service.agents.local_adapter import LocalAgentAdapter, LocalAgentConfig


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
