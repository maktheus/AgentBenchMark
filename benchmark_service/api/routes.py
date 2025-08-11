"""
Rotas da API REST
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/benchmark", tags=["benchmark"])

# Banco de dados simulado (em produção: PostgreSQL)
benchmark_runs = {}

class BenchmarkRequest(BaseModel):
    agents: List[str]
    benchmark: str
    config: Dict[str, Any] = None

@router.post("/run")
async def run_benchmark(request: BenchmarkRequest):
    run_id = str(uuid.uuid4())
    benchmark_runs[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "agents": request.agents,
        "benchmark": request.benchmark,
        "config": request.config
    }
    return benchmark_runs[run_id]

@router.get("/{run_id}")
async def get_benchmark_status(run_id: str):
    if run_id not in benchmark_runs:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return benchmark_runs[run_id]

@router.get("/list")
async def list_benchmarks():
    return [
        {
            "id": "mmlu-reasoning-v1",
            "name": "MMLU Reasoning Benchmark v1",
            "description": "Avaliação de raciocínio lógico baseada no MMLU",
            "categories": ["mathematics", "formal_logic"],
            "question_count": 150
        },
        {
            "id": "gsm8k-math-v2",
            "name": "GSM8K Math Benchmark v2",
            "description": "Problemas matemáticos de escola primária",
            "categories": ["arithmetic", "algebra"],
            "question_count": 850
        }
    ]
