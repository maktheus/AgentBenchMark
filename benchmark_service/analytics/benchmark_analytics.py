"""
Sistema de analytics para análise de benchmarks
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import json


class BenchmarkAnalytics:
    """Sistema de analytics para benchmarks"""

    def __init__(self):
        self.metrics_history = []

    def analyze_benchmark_results(
        self, benchmark_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisa os resultados de um benchmark e gera insights"""
        if not benchmark_results or "agents" not in benchmark_results:
            return {}

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_id": benchmark_results.get("benchmark", "unknown"),
            "total_agents": len(benchmark_results["agents"]),
            "performance_metrics": {},
            "comparative_analysis": {},
            "statistical_summary": {},
            "insights": [],
        }

        # Análise de métricas de performance
        performance_metrics = self._analyze_performance_metrics(
            benchmark_results["agents"]
        )
        analysis["performance_metrics"] = performance_metrics

        # Análise comparativa
        comparative_analysis = self._compare_agents(benchmark_results["agents"])
        analysis["comparative_analysis"] = comparative_analysis

        # Sumário estatístico
        statistical_summary = self._generate_statistical_summary(
            benchmark_results["agents"]
        )
        analysis["statistical_summary"] = statistical_summary

        # Insights automáticos
        insights = self._generate_insights(
            benchmark_results["agents"], performance_metrics
        )
        analysis["insights"] = insights

        # Armazenar no histórico
        self.metrics_history.append(analysis)

        return analysis

    def _analyze_performance_metrics(
        self, agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analisa métricas de performance individuais"""
        metrics_analysis = {}

        for agent in agents:
            agent_id = agent["id"]
            metrics = agent.get("metrics", {})

            metrics_analysis[agent_id] = {
                "accuracy_analysis": {
                    "value": metrics.get("accuracy", 0),
                    "rating": self._rate_accuracy(metrics.get("accuracy", 0)),
                },
                "latency_analysis": {
                    "value": metrics.get("latency_avg", 0),
                    "rating": self._rate_latency(metrics.get("latency_avg", 0)),
                },
                "efficiency_analysis": {
                    "tokens_per_second": self._calculate_tokens_per_second(
                        metrics.get("tokens_avg", 0), metrics.get("latency_avg", 0)
                    ),
                    "cost_efficiency": self._calculate_cost_efficiency(
                        metrics.get("accuracy", 0), metrics.get("tokens_avg", 0)
                    ),
                },
            }

        return metrics_analysis

    def _compare_agents(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compara performance entre agents"""
        if len(agents) < 2:
            return {"comparison_not_available": "Need at least 2 agents for comparison"}

        # Encontrar melhor desempenho em cada métrica
        accuracy_scores = {
            agent["id"]: agent["metrics"].get("accuracy", 0) for agent in agents
        }
        latency_scores = {
            agent["id"]: agent["metrics"].get("latency_avg", 0) for agent in agents
        }
        tokens_scores = {
            agent["id"]: agent["metrics"].get("tokens_avg", 0) for agent in agents
        }

        return {
            "best_accuracy": max(accuracy_scores, key=accuracy_scores.get),
            "best_latency": min(latency_scores, key=latency_scores.get),
            "most_efficient": min(tokens_scores, key=tokens_scores.get),
            "performance_ranking": self._rank_agents_by_performance(agents),
        }

    def _generate_statistical_summary(
        self, agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gera sumário estatístico dos resultados"""
        if not agents:
            return {}

        metrics_collection = defaultdict(list)

        # Coletar todas as métricas
        for agent in agents:
            metrics = agent.get("metrics", {})
            for key, value in metrics.items():
                metrics_collection[key].append(value)

        # Calcular estatísticas
        statistical_summary = {}
        for metric, values in metrics_collection.items():
            if values:
                statistical_summary[metric] = {
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "std_dev": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                }

        return statistical_summary

    def _generate_insights(
        self, agents: List[Dict[str, Any]], performance_metrics: Dict[str, Any]
    ) -> List[str]:
        """Gera insights automáticos baseados nos resultados"""
        insights = []

        for agent in agents:
            agent_id = agent["id"]
            metrics = agent.get("metrics", {})
            accuracy = metrics.get("accuracy", 0)
            latency = metrics.get("latency_avg", 0)
            tokens = metrics.get("tokens_avg", 0)

            # Insights baseados em accuracy
            if accuracy >= 90:
                insights.append(f"{agent_id} demonstra excelente precisão (≥90%)")
            elif accuracy >= 80:
                insights.append(f"{agent_id} mostra boa precisão (80-89%)")
            elif accuracy < 70:
                insights.append(f"{agent_id} precisa de melhorias na precisão (<70%)")

            # Insights baseados em latência
            if latency <= 2.0:
                insights.append(f"{agent_id} tem excelente tempo de resposta (≤2s)")
            elif latency > 5.0:
                insights.append(f"{agent_id} apresenta latência alta (>5s)")

            # Insights baseados em eficiência
            tokens_per_second = self._calculate_tokens_per_second(tokens, latency)
            if tokens_per_second > 500:
                insights.append(
                    f"{agent_id} é muito eficiente em processamento de tokens"
                )
            elif tokens_per_second < 100:
                insights.append(
                    f"{agent_id} poderia ser mais eficiente no processamento de tokens"
                )

        return insights

    def _rank_agents_by_performance(
        self, agents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Classifica agents por performance geral"""
        ranked_agents = []

        for agent in agents:
            agent_id = agent["id"]
            metrics = agent.get("metrics", {})

            # Calcular score composto (simplificado)
            accuracy_score = metrics.get("accuracy", 0) * 0.5
            latency_score = max(
                0, (10 - metrics.get("latency_avg", 0)) * 2
            )  # Normalizado
            consistency_score = metrics.get("consistency", 0) * 0.3

            composite_score = accuracy_score + latency_score + consistency_score

            ranked_agents.append(
                {
                    "agent_id": agent_id,
                    "composite_score": composite_score,
                    "accuracy": metrics.get("accuracy", 0),
                    "latency": metrics.get("latency_avg", 0),
                    "consistency": metrics.get("consistency", 0),
                }
            )

        # Ordenar por score composto
        ranked_agents.sort(key=lambda x: x["composite_score"], reverse=True)
        return ranked_agents

    def _rate_accuracy(self, accuracy: float) -> str:
        """Avalia a precisão"""
        if accuracy >= 90:
            return "Excellent"
        elif accuracy >= 80:
            return "Good"
        elif accuracy >= 70:
            return "Fair"
        else:
            return "Poor"

    def _rate_latency(self, latency: float) -> str:
        """Avalia a latência"""
        if latency <= 1.0:
            return "Excellent"
        elif latency <= 3.0:
            return "Good"
        elif latency <= 5.0:
            return "Fair"
        else:
            return "Poor"

    def _calculate_tokens_per_second(self, tokens: int, latency: float) -> float:
        """Calcula tokens por segundo"""
        if latency <= 0:
            return 0
        return tokens / latency if tokens > 0 else 0

    def _calculate_cost_efficiency(self, accuracy: float, tokens: int) -> float:
        """Calcula eficiência de custo (simplificada)"""
        if tokens <= 0:
            return 0
        # Normalizar accuracy e inverter tokens (menos tokens = mais eficiente)
        normalized_accuracy = accuracy / 100
        return normalized_accuracy / (tokens / 1000) if tokens > 0 else 0


# Instância global
benchmark_analytics = BenchmarkAnalytics()
