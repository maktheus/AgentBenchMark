"""
Testes end-to-end completos para o serviço de benchmark
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
import time

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


def test_complete_benchmark_execution_flow():
    """Teste completo do fluxo de execução de um benchmark"""
    # 1. Verificar que o serviço está saudável
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"

    # 2. Verificar readiness
    ready_response = client.get("/ready")
    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"

    # 3. Listar benchmarks disponíveis
    list_response = client.get("/api/benchmark/list")
    assert list_response.status_code == 200
    benchmarks = list_response.json()
    assert len(benchmarks) > 0

    # 4. Selecionar um benchmark para teste
    selected_benchmark = benchmarks[0]
    benchmark_id = selected_benchmark["id"]

    # 5. Submeter um novo benchmark para execução
    payload = {
        "agents": ["gpt-4-turbo", "claude-3-opus"],
        "benchmark": benchmark_id,
        "config": {"temperature": 0.7, "max_tokens": 1024},
    }

    submit_response = client.post("/api/benchmark/run", json=payload)
    assert submit_response.status_code == 200

    run_data = submit_response.json()
    run_id = run_data["run_id"]

    # Verificar dados iniciais do benchmark
    # O status pode ser 'queued' ou 'completed' dependendo da velocidade de processamento
    assert run_data["status"] in ["queued", "processing", "completed"]
    assert run_data["agents"] == payload["agents"]
    assert run_data["benchmark"] == payload["benchmark"]
    assert "created_at" in run_data

    # 6. Verificar status do benchmark
    status_response = client.get(f"/api/benchmark/{run_id}")
    assert status_response.status_code == 200

    status_data = status_response.json()
    assert status_data["run_id"] == run_id
    # O status pode ser 'queued' ou 'completed' dependendo da velocidade de processamento
    assert status_data["status"] in ["queued", "processing", "completed"]

    # 7. Simular processamento do benchmark
    # Em um ambiente real, isso seria feito pelo orquestrador
    benchmark_results[run_id] = {
        "run_id": run_id,
        "benchmark": benchmark_id,
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

    # 8. Verificar status atualizado
    updated_status_response = client.get(f"/api/benchmark/{run_id}")
    assert updated_status_response.status_code == 200

    updated_status_data = updated_status_response.json()
    # O status pode ser 'processing' ou 'completed' dependendo da velocidade de processamento
    assert updated_status_data["status"] in ["processing", "completed"]
    assert "results_url" in updated_status_data

    # 9. Obter resultados detalhados
    results_response = client.get(f"/api/benchmark/results/{run_id}")
    assert results_response.status_code == 200

    results_data = results_response.json()
    assert results_data["run_id"] == run_id
    assert results_data["benchmark"] == benchmark_id

    # Verificar estrutura dos resultados dos agents
    assert "agents" in results_data
    assert len(results_data["agents"]) == 2

    for agent_result in results_data["agents"]:
        assert "id" in agent_result
        assert "metrics" in agent_result
        assert "category_scores" in agent_result

        # Verificar métricas
        metrics = agent_result["metrics"]
        assert "accuracy" in metrics
        assert "latency_avg" in metrics
        assert "tokens_avg" in metrics
        assert "consistency" in metrics

        # Verificar scores por categoria
        category_scores = agent_result["category_scores"]
        assert "mathematics" in category_scores
        assert "logical_reasoning" in category_scores

    # Verificar sumário
    assert "summary" in results_data
    summary = results_data["summary"]
    assert "top_performer" in summary
    assert "critical_observations" in summary
    assert isinstance(summary["critical_observations"], list)

    # 10. Obter relatório em PDF
    report_response = client.get(f"/api/benchmark/results/{run_id}/report")
    assert report_response.status_code == 200
    assert report_response.headers["content-type"] == "application/pdf"
    assert (
        f"benchmark_report_{run_id}.pdf"
        in report_response.headers["content-disposition"]
    )

    # Verificar que o conteúdo não está vazio
    assert len(report_response.content) > 0


def test_complete_benchmark_execution_flow_with_local_agent():
    """Teste completo do fluxo de execução de um benchmark com agent local"""
    # 1. Verificar que o serviço está saudável
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"

    # 2. Verificar readiness
    ready_response = client.get("/ready")
    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"

    # 3. Listar benchmarks disponíveis
    list_response = client.get("/api/benchmark/list")
    assert list_response.status_code == 200
    benchmarks = list_response.json()
    assert len(benchmarks) > 0

    # 4. Selecionar um benchmark para teste
    selected_benchmark = benchmarks[0]
    benchmark_id = selected_benchmark["id"]

    # 5. Submeter um novo benchmark para execução com agent local
    payload = {
        "agents": ["local"],
        "benchmark": benchmark_id,
        "config": {"temperature": 0.7},
    }

    submit_response = client.post("/api/benchmark/run", json=payload)
    assert submit_response.status_code == 200

    run_data = submit_response.json()
    run_id = run_data["run_id"]

    # Verificar dados iniciais do benchmark
    # O status pode ser 'queued' ou 'completed' dependendo da velocidade de processamento
    assert run_data["status"] in ["queued", "processing", "completed"]
    assert run_data["agents"] == payload["agents"]
    assert run_data["benchmark"] == payload["benchmark"]

    # 6. Simular processamento do benchmark
    # Em um ambiente real, isso seria feito pelo orquestrador
    benchmark_results[run_id] = {
        "run_id": run_id,
        "benchmark": benchmark_id,
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

    # 7. Verificar status atualizado
    updated_status_response = client.get(f"/api/benchmark/{run_id}")
    assert updated_status_response.status_code == 200

    updated_status_data = updated_status_response.json()
    # O status pode ser 'processing' ou 'completed' dependendo da velocidade de processamento
    assert updated_status_data["status"] in ["processing", "completed"]
    assert "results_url" in updated_status_data

    # 8. Obter resultados detalhados
    results_response = client.get(f"/api/benchmark/results/{run_id}")
    assert results_response.status_code == 200

    results_data = results_response.json()
    assert results_data["run_id"] == run_id
    assert results_data["benchmark"] == benchmark_id
    assert len(results_data["agents"]) == 1
    assert results_data["agents"][0]["id"] == "local"

    # Verificar sumário
    assert "summary" in results_data
    summary = results_data["summary"]
    assert "top_performer" in summary
    assert summary["top_performer"] == "local"


def test_error_handling_for_nonexistent_benchmark():
    """Teste para verificar o tratamento de erros para benchmarks inexistentes"""
    fake_run_id = "00000000-0000-0000-0000-000000000000"

    # Tentar obter status de benchmark inexistente
    status_response = client.get(f"/api/benchmark/{fake_run_id}")
    assert status_response.status_code == 404
    assert status_response.json()["detail"] == "Benchmark not found"

    # Tentar obter resultados de benchmark inexistente
    results_response = client.get(f"/api/benchmark/results/{fake_run_id}")
    assert results_response.status_code == 404
    assert results_response.json()["detail"] == "Benchmark not found"

    # Tentar obter relatório de benchmark inexistente
    report_response = client.get(f"/api/benchmark/results/{fake_run_id}/report")
    assert report_response.status_code == 404
    assert report_response.json()["detail"] == "Benchmark not found"


def test_benchmark_with_minimal_config():
    """Teste para criar benchmark com configuração mínima"""
    payload = {
        "agents": ["local"],
        "benchmark": "gsm8k-math-v2",
        # Sem configuração adicional
    }

    response = client.post("/api/benchmark/run", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "run_id" in data
    assert data["agents"] == ["local"]
    assert data["benchmark"] == "gsm8k-math-v2"
    assert data["config"] is None  # Deve ser None quando não especificado
