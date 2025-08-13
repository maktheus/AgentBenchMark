"""
Testes de integração para a API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adicionar o diretório raiz ao path para importar o módulo principal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from benchmark_service.api.routes import benchmark_results

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Limpar o banco de dados simulado antes e depois de cada teste"""
    benchmark_results.clear()
    yield
    benchmark_results.clear()


def test_full_benchmark_workflow():
    """Teste completo do fluxo de um benchmark"""
    # 1. Criar um benchmark
    payload = {
        "agents": ["gpt-4-turbo", "claude-3-opus"],
        "benchmark": "mmlu-reasoning-v1",
        "config": {"temperature": 0.7},
    }

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # 2. Verificar status inicial
    status_response = client.get(f"/api/benchmark/{run_id}")
    assert status_response.status_code == 200
    # O status pode ser 'queued' ou 'completed' dependendo da velocidade de processamento
    assert status_response.json()["status"] in ["queued", "processing", "completed"]

    # 3. Simular conclusão do benchmark
    benchmark_results[run_id] = {
        "run_id": run_id,
        "benchmark": "mmlu-reasoning-v1",
        "agents": [
            {
                "id": "gpt-4-turbo",
                "metrics": {
                    "accuracy": 87.3,
                    "latency_avg": 4.2,
                    "tokens_avg": 1428,
                    "consistency": 4.7,
                },
                "category_scores": {"mathematics": 92.4, "logical_reasoning": 88.2},
            },
            {
                "id": "claude-3-opus",
                "metrics": {
                    "accuracy": 82.1,
                    "latency_avg": 6.8,
                    "tokens_avg": 1380,
                    "consistency": 4.3,
                },
                "category_scores": {"mathematics": 85.6, "logical_reasoning": 84.0},
            },
        ],
        "summary": {
            "top_performer": "gpt-4-turbo",
            "critical_observations": [
                "Melhor desempenho em raciocínio matemático",
                "Consistência superior em múltiplas categorias",
            ],
        },
    }

    # 4. Verificar status atualizado
    status_response = client.get(f"/api/benchmark/{run_id}")
    assert status_response.status_code == 200
    # O status pode ser 'processing' ou 'completed' dependendo da velocidade de processamento
    assert status_response.json()["status"] in ["processing", "completed"]
    assert "results_url" in status_response.json()

    # 5. Obter resultados
    results_response = client.get(f"/api/benchmark/results/{run_id}")
    assert results_response.status_code == 200

    results_data = results_response.json()
    assert results_data["run_id"] == run_id
    assert results_data["benchmark"] == "mmlu-reasoning-v1"
    assert len(results_data["agents"]) == 2
    assert "summary" in results_data

    # 6. Obter relatório
    report_response = client.get(f"/api/benchmark/results/{run_id}/report")
    assert report_response.status_code == 200
    assert report_response.headers["content-type"] == "application/pdf"


def test_full_benchmark_workflow_with_local_agent():
    """Teste completo do fluxo de um benchmark com agent local"""
    # 1. Criar um benchmark com agent local
    payload = {
        "agents": ["local"],
        "benchmark": "mmlu-reasoning-v1",
        "config": {"temperature": 0.7},
    }

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # 2. Verificar status inicial
    status_response = client.get(f"/api/benchmark/{run_id}")
    assert status_response.status_code == 200
    # O status pode ser 'queued' ou 'completed' dependendo da velocidade de processamento
    assert status_response.json()["status"] in ["queued", "processing", "completed"]

    # 3. Simular conclusão do benchmark
    benchmark_results[run_id] = {
        "run_id": run_id,
        "benchmark": "mmlu-reasoning-v1",
        "agents": [
            {
                "id": "local",
                "metrics": {
                    "accuracy": 75.0,
                    "latency_avg": 2.1,
                    "tokens_avg": 850,
                    "consistency": 4.0,
                },
                "category_scores": {"mathematics": 80.0, "logical_reasoning": 70.0},
            }
        ],
        "summary": {
            "top_performer": "local",
            "critical_observations": [
                "Desempenho consistente em raciocínio lógico",
                "Latência adequada para processamento local",
            ],
        },
    }

    # 4. Verificar status atualizado
    status_response = client.get(f"/api/benchmark/{run_id}")
    assert status_response.status_code == 200
    # O status pode ser 'processing' ou 'completed' dependendo da velocidade de processamento
    assert status_response.json()["status"] in ["processing", "completed"]
    assert "results_url" in status_response.json()

    # 5. Obter resultados
    results_response = client.get(f"/api/benchmark/results/{run_id}")
    assert results_response.status_code == 200

    results_data = results_response.json()
    assert results_data["run_id"] == run_id
    assert results_data["benchmark"] == "mmlu-reasoning-v1"
    assert len(results_data["agents"]) == 1
    assert results_data["agents"][0]["id"] == "local"
    assert "summary" in results_data


def test_list_benchmarks_endpoint():
    """Teste para verificar o endpoint de listagem de benchmarks"""
    response = client.get("/api/benchmark/list")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # Verificar que ambos os benchmarks esperados estão presentes
    benchmark_ids = [b["id"] for b in data]
    assert "mmlu-reasoning-v1" in benchmark_ids
    assert "gsm8k-math-v2" in benchmark_ids

    # Verificar estrutura de um benchmark
    mmlu_benchmark = next(b for b in data if b["id"] == "mmlu-reasoning-v1")
    assert mmlu_benchmark["name"] == "MMLU Reasoning Benchmark v1"
    assert "mathematics" in mmlu_benchmark["categories"]
    assert mmlu_benchmark["question_count"] == 150


def test_multiple_benchmarks_isolation():
    """Teste para verificar que múltiplos benchmarks são isolados corretamente"""
    # Criar dois benchmarks diferentes
    payload1 = {"agents": ["gpt-4-turbo"], "benchmark": "mmlu-reasoning-v1"}

    payload2 = {"agents": ["local"], "benchmark": "gsm8k-math-v2"}

    response1 = client.post("/api/benchmark/run", json=payload1)
    response2 = client.post("/api/benchmark/run", json=payload2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    run_id1 = response1.json()["run_id"]
    run_id2 = response2.json()["run_id"]

    # Verificar que são diferentes
    assert run_id1 != run_id2

    # Verificar status de cada um
    status1 = client.get(f"/api/benchmark/{run_id1}")
    status2 = client.get(f"/api/benchmark/{run_id2}")

    assert status1.status_code == 200
    assert status2.status_code == 200

    data1 = status1.json()
    data2 = status2.json()

    assert data1["run_id"] == run_id1
    assert data2["run_id"] == run_id2
    assert data1["agents"] == ["gpt-4-turbo"]
    assert data2["agents"] == ["local"]
