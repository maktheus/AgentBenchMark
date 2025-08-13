"""
Testes para o sistema de dedução de dados
"""

import pytest
from benchmark_service.analytics.data_deduction import DataDeductionEngine


def test_data_deduction_engine_initialization():
    """Testa a inicialização do motor de dedução de dados"""
    engine = DataDeductionEngine()
    assert engine is not None
    assert isinstance(engine.patterns, list)
    assert isinstance(engine.models, dict)


def test_deduct_patterns():
    """Testa a dedução de padrões"""
    engine = DataDeductionEngine()

    # Dados de teste
    benchmark_results = {
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
        ]
    }

    deductions = engine.deduct_patterns(benchmark_results)

    assert deductions is not None
    assert "performance_patterns" in deductions
    assert "behavioral_insights" in deductions
    assert "correlation_analysis" in deductions
    assert "anomaly_detection" in deductions
    assert "recommendations" in deductions


def test_performance_patterns_identification():
    """Testa identificação de padrões de performance"""
    engine = DataDeductionEngine()

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

    patterns = engine._identify_performance_patterns(agents)

    assert patterns is not None
    # Com apenas 2 agents, deve retornar um cluster simples
    assert "single_cluster" in patterns or "performance_clusters" in patterns


def test_behavioral_patterns_analysis():
    """Testa análise de padrões comportamentais"""
    engine = DataDeductionEngine()

    agents = [
        {
            "id": "test-agent",
            "metrics": {
                "accuracy": 88.0,
                "latency_avg": 2.1,
                "tokens_avg": 1100,
                "consistency": 4.3,
            },
            "category_scores": {
                "mathematics": 92.0,
                "logical_reasoning": 84.0,
                "language": 85.0,
            },
        }
    ]

    behavioral_patterns = engine._analyze_behavioral_patterns(agents)

    assert "test-agent" in behavioral_patterns
    agent_patterns = behavioral_patterns["test-agent"]

    assert "score_consistency" in agent_patterns
    assert "category_strengths" in agent_patterns
    assert "category_weaknesses" in agent_patterns
    assert "overall_performance_profile" in agent_patterns


def test_anomaly_detection():
    """Testa detecção de anomalias"""
    engine = DataDeductionEngine()

    # Criar dados com uma anomalia clara
    agents = [
        {
            "id": "normal-agent-1",
            "metrics": {
                "accuracy": 85.0,
                "latency_avg": 2.0,
                "tokens_avg": 1000,
                "consistency": 4.0,
            },
        },
        {
            "id": "normal-agent-2",
            "metrics": {
                "accuracy": 87.0,
                "latency_avg": 2.2,
                "tokens_avg": 1050,
                "consistency": 4.1,
            },
        },
        {
            "id": "anomaly-agent",
            "metrics": {
                "accuracy": 70.0,  # Valor muito baixo
                "latency_avg": 2.1,
                "tokens_avg": 1020,
                "consistency": 4.0,
            },
        },
    ]

    anomalies = engine._detect_anomalies(agents)

    assert "detected_anomalies" in anomalies
    # Deve detectar a anomalia no agente com accuracy muito baixa


def test_recommendations_generation():
    """Testa geração de recomendações"""
    engine = DataDeductionEngine()

    agents = [
        {
            "id": "low-performance-agent",
            "metrics": {
                "accuracy": 65.0,  # Baixa
                "latency_avg": 6.0,  # Alta
                "tokens_avg": 2500,  # Alta
                "consistency": 3.0,  # Baixa
            },
        }
    ]

    recommendations = engine._generate_recommendations(agents)

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    # Deve gerar recomendações para melhorar accuracy, latency e tokens
    assert any(
        "fine-tuning" in rec.lower() or "accuracy" in rec.lower()
        for rec in recommendations
    )
    assert any(
        "otimizar" in rec.lower() or "latency" in rec.lower() for rec in recommendations
    )
    assert any(
        "eficiência" in rec.lower() or "efficiency" in rec.lower()
        for rec in recommendations
    )
