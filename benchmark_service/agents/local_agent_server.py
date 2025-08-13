"""
Servidor de exemplo para agent local
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import time
import random

app = FastAPI(
    title="Local Agent Server", description="Servidor de exemplo para agent local"
)


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "local-model"
    temperature: float = 0.7
    max_tokens: int = 1024


class ChatResponse(BaseModel):
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    model: str


@app.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint para chat com o agent local"""
    # Simular processamento
    prompt = request.messages[-1]["content"] if request.messages else ""

    # Simular tempo de processamento
    time.sleep(0.1 + random.uniform(0.05, 0.2))

    # Gerar resposta baseada no prompt
    response_text = generate_local_response(prompt)

    # Calcular tokens
    input_tokens = len(prompt.split())
    output_tokens = len(response_text.split())

    return ChatResponse(
        choices=[{"message": {"role": "assistant", "content": response_text}}],
        usage={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
        model=request.model,
    )


def generate_local_response(prompt: str) -> str:
    """Gera uma resposta simulada para o prompt"""
    if "math" in prompt.lower() or "calculate" in prompt.lower():
        return "I've analyzed the mathematical problem. The solution involves applying the quadratic formula, which gives us the result of 42 as the primary solution."
    elif "reasoning" in prompt.lower() or "logic" in prompt.lower():
        return "Through careful logical analysis, I can conclude that the premises lead to the inevitable conclusion that all logical paths converge at this point."
    elif "question" in prompt.lower():
        return "This is a thoughtful response to your query. After considering multiple perspectives and relevant information, I can provide this comprehensive answer."
    else:
        return "As a locally hosted AI assistant, I specialize in providing detailed and accurate responses to a wide variety of questions and tasks. How can I assist you further?"


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "model": "local-model-v1"}


@app.get("/info")
async def get_info():
    """Endpoint com informações do agent"""
    return {
        "name": "local-agent",
        "version": "1.0.0",
        "capabilities": ["text-generation", "reasoning", "problem-solving"],
        "model": "local-model-v1",
    }


if __name__ == "__main__":
    uvicorn.run("local_agent_server:app", host="0.0.0.0", port=8001, reload=True)
