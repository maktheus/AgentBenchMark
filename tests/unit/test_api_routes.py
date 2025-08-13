"""
Testes unitários para as rotas da API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
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


def test_health_check():
    """Teste para o endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness_check():
    """Teste para o endpoint de readiness check"""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_run_benchmark():
    """Teste para criar um novo benchmark"""
    payload = {
        "agents": ["gpt-4-turbo", "claude-3-opus"],
        "benchmark": "mmlu-reasoning-v1",
        "config": {"temperature": 0.7, "max_tokens": 1024},
    }

    response = client.post("/api/benchmark/run", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "run_id" in data
    assert data["status"] == "queued"
    assert data["agents"] == payload["agents"]
    assert data["benchmark"] == payload["benchmark"]
    assert data["config"] == payload["config"]


def test_run_benchmark_with_local_agent():
    """Teste para criar um novo benchmark com agent local"""
    payload = {
        "agents": ["local"],
        "benchmark": "mmlu-reasoning-v1",
        "config": {"temperature": 0.7},
    }

    response = client.post("/api/benchmark/run", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "run_id" in data
    assert data["status"] == "queued"
    assert data["agents"] == payload["agents"]
    assert data["benchmark"] == payload["benchmark"]


def test_get_benchmark_status_success():
    """Teste para obter o status de um benchmark existente"""
    # Primeiro criar um benchmark
    payload = {"agents": ["gpt-4-turbo"], "benchmark": "gsm8k-math-v2"}

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # Agora buscar o status
    response = client.get(f"/api/benchmark/{run_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["run_id"] == run_id
    # O status pode ser 'queued' ou 'completed' dependendo da velocidade de processamento
    assert data["status"] in ["queued", "processing", "completed"]


def test_get_benchmark_status_not_found():
    """Teste para tentar obter o status de um benchmark inexistente"""
    response = client.get("/api/benchmark/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Benchmark not found"


def test_list_benchmarks():
    """Teste para listar benchmarks disponíveis"""
    response = client.get("/api/benchmark/list")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # Verificar estrutura do primeiro benchmark
    first_benchmark = data[0]
    assert "id" in first_benchmark
    assert "name" in first_benchmark
    assert "description" in first_benchmark
    assert "categories" in first_benchmark
    assert "question_count" in first_benchmark


def test_get_benchmark_results_success():
    """Teste para obter resultados de um benchmark concluído"""
    # Criar um benchmark
    payload = {
        "agents": ["gpt-4-turbo", "claude-3-opus"],
        "benchmark": "mmlu-reasoning-v1",
    }

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # Simular conclusão do benchmark
    # Em produção, isso seria feito pelo worker
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
            }
        ],
        "summary": {
            "top_performer": "gpt-4-turbo",
            "critical_observations": [
                "Melhor desempenho em raciocínio matemático",
                "Consistência superior em múltiplas categorias",
            ],
        },
    }

    # Agora buscar os resultados
    response = client.get(f"/api/benchmark/results/{run_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["run_id"] == run_id
    assert data["benchmark"] == "mmlu-reasoning-v1"
    assert "agents" in data
    assert "summary" in data


def test_get_benchmark_analysis():
    """Teste para obter análise de um benchmark concluído"""
    # Criar um benchmark
    payload = {"agents": ["gpt-4-turbo"], "benchmark": "mmlu-reasoning-v1"}

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # Simular conclusão do benchmark com análise
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
            }
        ],
        "summary": {
            "top_performer": "gpt-4-turbo",
            "critical_observations": [
                "Melhor desempenho em raciocínio matemático",
                "Consistência superior em múltiplas categorias",
            ],
        },
        "analysis": {
            "performance_insights": "Análise detalhada de performance",
            "recommendations": ["Otimizar latência", "Melhorar eficiência de tokens"],
        },
    }

    # Agora buscar a análise
    response = client.get(f"/api/benchmark/results/{run_id}/analysis")
    assert response.status_code == 200

    data = response.json()
    assert "performance_insights" in data
    assert "recommendations" in data


def test_get_benchmark_deductions():
    """Teste para obter deduções de um benchmark concluído"""
    # Criar um benchmark
    payload = {"agents": ["gpt-4-turbo"], "benchmark": "mmlu-reasoning-v1"}

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # Simular conclusão do benchmark com deduções
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
            }
        ],
        "summary": {
            "top_performer": "gpt-4-turbo",
            "critical_observations": [
                "Melhor desempenho em raciocínio matemático",
                "Consistência superior em múltiplas categorias",
            ],
        },
        "deductions": {
            "patterns": "Padrões identificados na performance",
            "correlations": "Correlações entre métricas",
        },
    }

    # Agora buscar as deduções
    response = client.get(f"/api/benchmark/results/{run_id}/deductions")
    assert response.status_code == 200

    data = response.json()
    assert "patterns" in data
    assert "correlations" in data


def test_get_benchmark_results_not_found():
    """Teste para tentar obter resultados de um benchmark inexistente"""
    response = client.get("/api/benchmark/results/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Benchmark not found"


def test_get_benchmark_results_not_available():
    """Teste para tentar obter resultados de um benchmark que ainda não terminou"""
    # Criar um benchmark
    payload = {"agents": ["gpt-4-turbo"], "benchmark": "gsm8k-math-v2"}

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # Para este teste, vamos remover temporariamente os resultados para simular
    # um benchmark que ainda não terminou
    original_results = dict(benchmark_results)
    benchmark_results.clear()

    # Tentar obter resultados antes de concluir o benchmark
    response = client.get(f"/api/benchmark/results/{run_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Results not available yet"

    # Restaurar os resultados
    benchmark_results.update(original_results)


def test_get_benchmark_report():
    """Teste para obter o relatório PDF de um benchmark"""
    # Criar um benchmark
    payload = {"agents": ["gpt-4-turbo"], "benchmark": "mmlu-reasoning-v1"}

    create_response = client.post("/api/benchmark/run", json=payload)
    assert create_response.status_code == 200

    run_id = create_response.json()["run_id"]

    # Buscar o relatório
    response = client.get(f"/api/benchmark/results/{run_id}/report")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f"benchmark_report_{run_id}.pdf" in response.headers["content-disposition"]


def test_get_benchmark_report_not_found():
    """Teste para tentar obter o relatório de um benchmark inexistente"""
    response = client.get("/api/benchmark/results/non-existent-id/report")
    assert response.status_code == 404
    assert response.json()["detail"] == "Benchmark not found"


def test_get_analytics_history():
    """Teste para obter histórico de análises"""
    response = client.get("/api/benchmark/analytics/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
