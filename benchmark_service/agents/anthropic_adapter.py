"""
Adapter para Anthropic API
"""

import httpx
import os
from typing import Dict, Any
from pydantic import BaseModel
from .base import AgentInterface


class AnthropicConfig(BaseModel):
    api_key: str
    model: str = "claude-3-opus-20240229"
    temperature: float = 0.7
    max_tokens: int = 1024


class AnthropicAgentAdapter(AgentInterface):
    def __init__(self, config: AnthropicConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            timeout=30.0,
        )

    async def query(
        self, prompt: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages", json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                "response": data["content"][0]["text"],
                "usage": {
                    "input_tokens": data.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": data.get("usage", {}).get("output_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("input_tokens", 0)
                    + data.get("usage", {}).get("output_tokens", 0),
                },
                "latency": response.elapsed.total_seconds(),
            }

        except httpx.HTTPStatusError as e:
            return {
                "error": f"API Error {e.response.status_code}",
                "raw_response": e.response.text,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "anthropic",
            "model": self.config.model,
            "capabilities": ["text-generation", "reasoning", "analysis"],
        }
