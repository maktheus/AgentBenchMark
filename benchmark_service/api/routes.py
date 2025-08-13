"""
Rotas da API REST
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from ..services.benchmark_service import BenchmarkService
from ..models import BenchmarkRequest
from ..analytics.benchmark_analytics import benchmark_analytics

router = APIRouter(prefix="/benchmark", tags=["benchmark"])

# Serviço de benchmark
benchmark_service = BenchmarkService()

# Banco de dados simulado (em produção: PostgreSQL)
benchmark_results = {}


# Rotas para benchmarks
@router.post("/run")
async def run_benchmark(request: BenchmarkRequest):
    run_id = await benchmark_service.start_benchmark(
        agents=request.agents, benchmark=request.benchmark, config=request.config
    )

    # Em produção, isso seria feito por um orquestrador
    # Por enquanto, vamos simular o processamento
    import asyncio

    asyncio.create_task(simulate_benchmark_processing(run_id, request))

    # Get the status and map fields to match expected response
    status = benchmark_service.get_run_status(run_id)
    if status:
        # Map benchmark_type to benchmark
        status["benchmark"] = status.pop("benchmark_type", request.benchmark)
        # Add results_url field
        status["results_url"] = f"/api/benchmark/results/{run_id}"
    return status


@router.get("/list")
async def list_benchmarks():
    return [
        {
            "id": "mmlu-reasoning-v1",
            "name": "MMLU Reasoning Benchmark v1",
            "description": "Avaliação de raciocínio lógico baseada no MMLU",
            "categories": ["mathematics", "formal_logic"],
            "question_count": 150,
        },
        {
            "id": "gsm8k-math-v2",
            "name": "GSM8K Math Benchmark v2",
            "description": "Problemas matemáticos de escola primária",
            "categories": ["arithmetic", "algebra"],
            "question_count": 850,
        },
    ]


@router.get("/{run_id}")
async def get_benchmark_status(run_id: str):
    status = benchmark_service.get_run_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    # Map benchmark_type to benchmark
    status["benchmark"] = status.pop("benchmark_type", "")
    # Add results_url field if benchmark is completed
    if status.get("status") == "completed":
        status["results_url"] = f"/api/benchmark/results/{run_id}"
    return status


# Novas rotas para resultados
@router.get("/results/{run_id}")
async def get_benchmark_results(run_id: str):
    status = benchmark_service.get_run_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    # Se não houver resultados ainda, retornar um erro apropriado
    if run_id not in benchmark_results:
        raise HTTPException(status_code=404, detail="Results not available yet")

    return benchmark_results[run_id]


@router.get("/results/{run_id}/analysis")
async def get_benchmark_analysis(run_id: str):
    """Obtém análise detalhada dos resultados do benchmark"""
    status = benchmark_service.get_run_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    # Se não houver resultados ainda, retornar um erro apropriado
    if run_id not in benchmark_results:
        raise HTTPException(status_code=404, detail="Results not available yet")

    results = benchmark_results[run_id]
    if "analysis" not in results:
        raise HTTPException(
            status_code=404, detail="Analysis not available for this benchmark"
        )

    return results["analysis"]


@router.get("/results/{run_id}/deductions")
async def get_benchmark_deductions(run_id: str):
    """Obtém deduções avançadas dos resultados do benchmark"""
    status = benchmark_service.get_run_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    # Se não houver resultados ainda, retornar um erro apropriado
    if run_id not in benchmark_results:
        raise HTTPException(status_code=404, detail="Results not available yet")

    results = benchmark_results[run_id]
    if "deductions" not in results:
        raise HTTPException(
            status_code=404, detail="Deductions not available for this benchmark"
        )

    return results["deductions"]


@router.get("/results/{run_id}/report")
async def get_benchmark_report(run_id: str):
    status = benchmark_service.get_run_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    # Simular um PDF de relatório
    pdf_content = f"Relatório de Benchmark para run_id: {run_id}".encode()

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=benchmark_report_{run_id}.pdf"
        },
    )


@router.get("/analytics/history")
async def get_analytics_history():
    """Obtém histórico de análises de benchmarks"""
    return benchmark_analytics.metrics_history


# Função auxiliar para simular a conclusão de um benchmark e geração de resultados
async def simulate_benchmark_processing(run_id: str, request: BenchmarkRequest):
    """Função auxiliar para simular o processamento assíncrono de um benchmark"""
    await benchmark_service.start_processing(run_id)

    # Simular processamento
    await benchmark_service.update_progress(run_id, 0.5)

    # Criar resultados simulados com análise
    benchmark_results[run_id] = {
        "run_id": run_id,
        "benchmark": request.benchmark,
        "agents": [
            {
                "id": agent,
                "metrics": {
                    "accuracy": 87.3,
                    "latency_avg": 4.2,
                    "tokens_avg": 1428,
                    "consistency": 4.7,
                },
                "category_scores": {"mathematics": 92.4, "logical_reasoning": 88.2},
            }
            for agent in request.agents
        ],
        "summary": {
            "top_performer": request.agents[0] if request.agents else "none",
            "critical_observations": [
                "Melhor desempenho em raciocínio matemático",
                "Consistência superior em múltiplas categorias",
            ],
        },
        "analysis": {
            "performance_insights": "Análise detalhada de performance",
            "recommendations": ["Otimizar latência", "Melhorar eficiência de tokens"],
        },
        "deductions": {
            "patterns": "Padrões identificados na performance",
            "correlations": "Correlações entre métricas",
        },
    }

    # Completar o benchmark
    await benchmark_service.complete_benchmark(run_id, benchmark_results[run_id])
