"""
Evaluators para análise de resultados de benchmarks
"""

from typing import Dict, Any, List
from collections import defaultdict


class BenchmarkEvaluator:
    """Avaliador de resultados de benchmarks"""

    def evaluate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia os resultados do benchmark e gera métricas"""
        if not results:
            return {}

        # Organizar resultados por agent
        agent_stats = defaultdict(
            lambda: {
                "total_questions": 0,
                "correct_answers": 0,
                "total_latency": 0.0,
                "total_tokens": 0,
                "errors": 0,
            }
        )

        # Processar cada resultado
        for result in results:
            for agent_response in result.get("agent_responses", []):
                agent_name = agent_response["agent"]
                stats = agent_stats[agent_name]

                stats["total_questions"] += 1

                if "error" in agent_response:
                    stats["errors"] += 1
                else:
                    if agent_response.get("correct", False):
                        stats["correct_answers"] += 1

                    # Coletar métricas de desempenho
                    response_data = agent_response.get("response", {})
                    if isinstance(response_data, dict):
                        if "latency" in response_data:
                            stats["total_latency"] += response_data["latency"]
                        if (
                            "usage" in response_data
                            and "total_tokens" in response_data["usage"]
                        ):
                            stats["total_tokens"] += response_data["usage"][
                                "total_tokens"
                            ]

        # Calcular métricas finais
        evaluated_results = {}
        for agent_name, stats in agent_stats.items():
            accuracy = (
                (stats["correct_answers"] / stats["total_questions"] * 100)
                if stats["total_questions"] > 0
                else 0
            )
            avg_latency = (
                (stats["total_latency"] / stats["total_questions"])
                if stats["total_questions"] > 0
                else 0
            )
            avg_tokens = (
                (stats["total_tokens"] / stats["total_questions"])
                if stats["total_questions"] > 0
                else 0
            )
            error_rate = (
                (stats["errors"] / stats["total_questions"] * 100)
                if stats["total_questions"] > 0
                else 0
            )

            evaluated_results[agent_name] = {
                "metrics": {
                    "accuracy": round(accuracy, 2),
                    "latency_avg": round(avg_latency, 2),
                    "tokens_avg": round(avg_tokens, 2),
                    "error_rate": round(error_rate, 2),
                    "consistency": round(100 - error_rate, 2),  # Simplificação
                },
                "raw_stats": stats,
            }

        return evaluated_results


class LLMEvaluator:
    """Evaluator que usa LLM como juiz para avaliação subjetiva"""

    def evaluate_quality(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia a qualidade das respostas usando LLM-as-a-Judge"""
        # Esta é uma implementação simplificada
        # Em produção, isso faria chamadas reais para um modelo de julgamento

        quality_scores = {}
        for response in responses:
            agent_name = response.get("agent", "unknown")
            response_text = (
                response.get("response", {}).get("response", "")
                if isinstance(response.get("response"), dict)
                else ""
            )

            # Simulação de avaliação de qualidade
            # Em produção, isso usaria um modelo real
            quality_score = min(5.0, len(response_text) / 100.0)  # Simplificação

            quality_scores[agent_name] = {
                "coherence": round(quality_score, 2),
                "relevance": round(quality_score * 0.9, 2),
                "completeness": round(quality_score * 0.8, 2),
            }

        return quality_scores


# Instâncias globais
benchmark_evaluator = BenchmarkEvaluator()
llm_evaluator = LLMEvaluator()
