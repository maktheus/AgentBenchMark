"""
Testes para os evaluators
"""

import pytest
from benchmark_service.evaluators.benchmark_evaluator import (
    BenchmarkEvaluator,
    LLMEvaluator,
)


def test_benchmark_evaluator():
    """Testa o avaliador de benchmarks"""
    evaluator = BenchmarkEvaluator()

    # Dados de teste
    results = [
        {
            "question_id": "math-001",
            "agent_responses": [
                {
                    "agent": "gpt-4-turbo",
                    "response": {
                        "response": "Correct answer",
                        "latency": 1.5,
                        "usage": {"total_tokens": 100},
                    },
                    "correct": True,
                },
                {
                    "agent": "claude-3-opus",
                    "response": {
                        "response": "Wrong answer",
                        "latency": 2.0,
                        "usage": {"total_tokens": 120},
                    },
                    "correct": False,
                },
            ],
        }
    ]

    evaluated = evaluator.evaluate_results(results)

    assert "gpt-4-turbo" in evaluated
    assert "claude-3-opus" in evaluated

    # Verificar métricas do GPT-4
    gpt_metrics = evaluated["gpt-4-turbo"]["metrics"]
    assert gpt_metrics["accuracy"] == 100.0
    assert gpt_metrics["latency_avg"] == 1.5
    assert gpt_metrics["tokens_avg"] == 100.0
    assert gpt_metrics["error_rate"] == 0.0

    # Verificar métricas do Claude
    claude_metrics = evaluated["claude-3-opus"]["metrics"]
    assert claude_metrics["accuracy"] == 0.0
    assert claude_metrics["latency_avg"] == 2.0
    assert claude_metrics["tokens_avg"] == 120.0
    assert (
        claude_metrics["error_rate"] == 0.0
    )  # Não há erros, apenas respostas incorretas


def test_llm_evaluator():
    """Testa o avaliador LLM"""
    evaluator = LLMEvaluator()

    responses = [
        {
            "agent": "gpt-4-turbo",
            "response": {
                "response": "This is a detailed and comprehensive answer that covers multiple aspects of the question."
            },
        },
        {"agent": "claude-3-opus", "response": {"response": "Short answer"}},
    ]

    quality_scores = evaluator.evaluate_quality(responses)

    assert "gpt-4-turbo" in quality_scores
    assert "claude-3-opus" in quality_scores

    gpt_quality = quality_scores["gpt-4-turbo"]
    assert "coherence" in gpt_quality
    assert "relevance" in gpt_quality
    assert "completeness" in gpt_quality
