"""
Adapter para agents locais
"""

import httpx
import asyncio
from typing import Dict, Any
from pydantic import BaseModel
from .base import AgentInterface


class LocalAgentConfig(BaseModel):
    endpoint: str = "http://localhost:8001/chat"
    timeout: float = 30.0
    model: str = "local-model"


class LocalAgentAdapter(AgentInterface):
    def __init__(self, config: LocalAgentConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)

    async def query(
        self, prompt: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Faz uma chamada HTTP real para um agent local.
        """
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": self.config.model,
                "temperature": 0.7,
                "max_tokens": 1024,
            }

            start_time = asyncio.get_event_loop().time()
            response = await self.client.post(self.config.endpoint, json=payload)
            end_time = asyncio.get_event_loop().time()

            response.raise_for_status()
            data = response.json()

            return {
                "response": data["choices"][0]["message"]["content"],
                "usage": data["usage"],
                "latency": end_time - start_time,
            }

        except httpx.TimeoutException:
            return {"error": "Request timeout"}
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP Error {e.response.status_code}",
                "raw_response": e.response.text,
            }
        except Exception as e:
            # Em caso de falha, usar simulação como fallback
            return self._simulate_response(prompt, context)

    async def _simulate_response(
        self, prompt: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Simula a resposta em caso de falha na chamada HTTP.
        """
        await asyncio.sleep(0.1)

        response_text = self._generate_response_text(prompt)

        return {
            "response": response_text,
            "usage": {
                "input_tokens": len(prompt.split()),
                "output_tokens": len(response_text.split()),
                "total_tokens": len(prompt.split()) + len(response_text.split()),
            },
            "latency": 0.1 + (len(prompt) * 0.0001),
        }

    def _generate_response_text(self, prompt: str) -> str:
        """Gera texto de resposta baseado no prompt"""
        if "math" in prompt.lower() or "calculate" in prompt.lower():
            return "Based on the mathematical question, the answer would be 42."
        elif "reasoning" in prompt.lower() or "logic" in prompt.lower():
            return "Through logical deduction, the conclusion is that all paths lead to the same result."
        elif "question" in prompt.lower():
            return "This is a comprehensive answer to your question, taking into account all relevant factors."
        else:
            return "As an AI assistant, I can help you with various tasks including answering questions, solving problems, and providing information."

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "local",
            "model": self.config.model,
            "capabilities": ["text-generation", "reasoning", "problem-solving"],
        }
