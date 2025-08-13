"""
Testes para o serviço de benchmark
"""

import pytest
from unittest.mock import patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from benchmark_service.services.benchmark_service import BenchmarkService


@pytest.mark.asyncio
async def test_start_benchmark():
    """Testa a criação de um novo benchmark"""
    service = BenchmarkService()

    run_id = await service.start_benchmark(
        agents=["gpt-4-turbo", "claude-3-opus"],
        benchmark="mmlu-reasoning-v1",
        config={"temperature": 0.7},
    )

    assert run_id is not None
    assert len(run_id) > 0

    # Verificar status
    status = service.get_run_status(run_id)
    assert status["run_id"] == run_id
    assert status["status"] == "queued"
    assert status["agents"] == ["gpt-4-turbo", "claude-3-opus"]
    assert status["benchmark"] == "mmlu-reasoning-v1"
    assert status["config"] == {"temperature": 0.7}


def test_get_run_status_not_found():
    """Testa obtenção de status de benchmark inexistente"""
    service = BenchmarkService()

    status = service.get_run_status("non-existent-id")
    assert status is None


@pytest.mark.asyncio
async def test_benchmark_lifecycle():
    """Testa o ciclo de vida completo de um benchmark"""
    service = BenchmarkService()

    # Criar benchmark
    run_id = await service.start_benchmark(
        agents=["gpt-4-turbo"], benchmark="gsm8k-math-v2"
    )

    # Verificar status inicial
    status = service.get_run_status(run_id)
    assert status["status"] == "queued"

    # Iniciar processamento
    await service.start_processing(run_id)
    status = service.get_run_status(run_id)
    assert status["status"] == "processing"
    assert status["started_at"] is not None

    # Atualizar progresso
    await service.update_progress(run_id, 0.5)
    status = service.get_run_status(run_id)
    assert status["progress"] == 0.5

    # Completar benchmark
    await service.complete_benchmark(run_id, [])
    status = service.get_run_status(run_id)
    assert status["status"] == "completed"
    assert status["progress"] == 1.0
    assert status["completed_at"] is not None
    assert status["results_url"] == f"/api/benchmark/results/{run_id}"
