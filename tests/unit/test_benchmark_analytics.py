"""
Testes para o sistema de analytics
"""

import pytest
from benchmark_service.analytics.benchmark_analytics import BenchmarkAnalytics


def test_benchmark_analytics_initialization():
    """Testa a inicialização do sistema de analytics"""
    analytics = BenchmarkAnalytics()
    assert analytics is not None
    assert isinstance(analytics.metrics_history, list)


def test_analyze_benchmark_results():
    """Testa análise de resultados de benchmark"""
    analytics = BenchmarkAnalytics()

    # Dados de teste
    benchmark_results = {
        "benchmark": "test-benchmark",
        "agents": [
            {
                "id": "agent-1",
                "metrics": {
                    "accuracy": 85.5,
                    "latency_avg": 2.3,
                    "tokens_avg": 1200,
                    "consistency": 4.2,
                },
                "category_scores": {"mathematics": 88.0, "logical_reasoning": 83.0},
            },
            {
                "id": "agent-2",
                "metrics": {
                    "accuracy": 92.0,
                    "latency_avg": 1.8,
                    "tokens_avg": 1100,
                    "consistency": 4.7,
                },
                "category_scores": {"mathematics": 95.0, "logical_reasoning": 89.0},
            },
        ],
    }

    analysis = analytics.analyze_benchmark_results(benchmark_results)

    assert analysis is not None
    assert "timestamp" in analysis
    assert analysis["benchmark_id"] == "test-benchmark"
    assert analysis["total_agents"] == 2
    assert "performance_metrics" in analysis
    assert "comparative_analysis" in analysis
    assert "statistical_summary" in analysis
    assert "insights" in analysis


def test_performance_metrics_analysis():
    """Testa análise de métricas de performance"""
    analytics = BenchmarkAnalytics()

    agents = [
        {
            "id": "test-agent",
            "metrics": {
                "accuracy": 95.0,
                "latency_avg": 1.5,
                "tokens_avg": 800,
                "consistency": 4.8,
            },
        }
    ]

    performance_metrics = analytics._analyze_performance_metrics(agents)

    assert "test-agent" in performance_metrics
    agent_metrics = performance_metrics["test-agent"]

    assert "accuracy_analysis" in agent_metrics
    assert "latency_analysis" in agent_metrics
    assert "efficiency_analysis" in agent_metrics

    # Verificar ratings
    assert agent_metrics["accuracy_analysis"]["rating"] == "Excellent"
    assert (
        agent_metrics["latency_analysis"]["rating"] == "Good"
    )  # 1.5s é Good, não Excellent


def test_comparative_analysis():
    """Testa análise comparativa entre agents"""
    analytics = BenchmarkAnalytics()

    agents = [
        {
            "id": "agent-a",
            "metrics": {
                "accuracy": 85.0,
                "latency_avg": 2.0,
                "tokens_avg": 1000,
                "consistency": 4.0,
            },
        },
        {
            "id": "agent-b",
            "metrics": {
                "accuracy": 92.0,
                "latency_avg": 1.5,
                "tokens_avg": 1200,
                "consistency": 4.5,
            },
        },
    ]

    comparative_analysis = analytics._compare_agents(agents)

    assert "best_accuracy" in comparative_analysis
    assert "best_latency" in comparative_analysis
    assert "most_efficient" in comparative_analysis
    assert "performance_ranking" in comparative_analysis

    assert comparative_analysis["best_accuracy"] == "agent-b"
    assert comparative_analysis["best_latency"] == "agent-b"


def test_statistical_summary():
    """Testa geração de sumário estatístico"""
    analytics = BenchmarkAnalytics()

    agents = [
        {"id": "agent-1", "metrics": {"accuracy": 80.0, "latency_avg": 2.0}},
        {"id": "agent-2", "metrics": {"accuracy": 90.0, "latency_avg": 1.0}},
    ]

    statistical_summary = analytics._generate_statistical_summary(agents)

    assert "accuracy" in statistical_summary
    assert "latency_avg" in statistical_summary

    accuracy_stats = statistical_summary["accuracy"]
    assert "mean" in accuracy_stats
    assert "median" in accuracy_stats
    assert "std_dev" in accuracy_stats
    assert accuracy_stats["mean"] == 85.0
    assert accuracy_stats["median"] == 85.0


def test_insights_generation():
    """Testa geração de insights"""
    analytics = BenchmarkAnalytics()

    agents = [
        {
            "id": "high-accuracy-agent",
            "metrics": {
                "accuracy": 95.0,
                "latency_avg": 3.0,
                "tokens_avg": 1500,
                "consistency": 4.9,
            },
        }
    ]

    performance_metrics = analytics._analyze_performance_metrics(agents)
    insights = analytics._generate_insights(agents, performance_metrics)

    assert isinstance(insights, list)
    assert len(insights) > 0
    assert any(
        "excelente precisão" in insight or "excellent accuracy" in insight.lower()
        for insight in insights
    )
