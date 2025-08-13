"""
Adapter para OpenAI API
"""

import httpx
import os
from typing import Dict, Any
from pydantic import BaseModel
from .base import AgentInterface


class OpenAIConfig(BaseModel):
    api_key: str
    model: str = "gpt-4-turbo"
    temperature: float = 0.7
    max_tokens: int = 1024


class OpenAIAgentAdapter(AgentInterface):
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {config.api_key}"}, timeout=30.0
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
                "https://api.openai.com/v1/chat/completions", json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                "response": data["choices"][0]["message"]["content"],
                "usage": data["usage"],
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
            "name": "openai",
            "model": self.config.model,
            "capabilities": ["text-generation", "reasoning"],
        }
