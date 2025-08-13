"""
Agents Package
"""

from .base import AgentInterface
from .openai_adapter import OpenAIAgentAdapter, OpenAIConfig
from .anthropic_adapter import AnthropicAgentAdapter, AnthropicConfig
from .local_adapter import LocalAgentAdapter, LocalAgentConfig

# Registro de adapters disponíveis
AGENT_ADAPTERS = {
    "openai": OpenAIAgentAdapter,
    "anthropic": AnthropicAgentAdapter,
    "local": LocalAgentAdapter,
}

AGENT_CONFIGS = {
    "openai": OpenAIConfig,
    "anthropic": AnthropicConfig,
    "local": LocalAgentConfig,
}
