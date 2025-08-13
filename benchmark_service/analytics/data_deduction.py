"""
Sistema de dedução de dados para análise avançada de benchmarks
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import json


class DataDeductionEngine:
    """Motor de dedução de dados para análise avançada"""

    def __init__(self):
        self.patterns = []
        self.models = {}

    def deduct_patterns(self, benchmark_results: Dict[str, Any]) -> Dict[str, Any]:
        """Deduz padrões e insights avançados dos resultados"""
        if not benchmark_results or "agents" not in benchmark_results:
            return {}

        deductions = {
            "performance_patterns": self._identify_performance_patterns(
                benchmark_results["agents"]
            ),
            "behavioral_insights": self._analyze_behavioral_patterns(
                benchmark_results["agents"]
            ),
            "correlation_analysis": self._analyze_metric_correlations(
                benchmark_results["agents"]
            ),
            "anomaly_detection": self._detect_anomalies(benchmark_results["agents"]),
            "recommendations": self._generate_recommendations(
                benchmark_results["agents"]
            ),
        }

        return deductions

    def _identify_performance_patterns(
        self, agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identifica padrões de performance"""
        if len(agents) < 2:
            return {"insufficient_data": "Need at least 2 agents for pattern analysis"}

        # Extrair métricas para análise
        metrics_data = []
        agent_names = []

        for agent in agents:
            metrics = agent.get("metrics", {})
            agent_names.append(agent["id"])

            # Criar vetor de características
            feature_vector = [
                metrics.get("accuracy", 0),
                metrics.get("latency_avg", 0),
                metrics.get("tokens_avg", 0),
                metrics.get("consistency", 0),
            ]
            metrics_data.append(feature_vector)

        # Clusterização para identificar grupos de performance
        try:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(metrics_data)

            # Determinar número ótimo de clusters (simplificado)
            n_clusters = min(3, len(agents))
            if n_clusters >= 2:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(scaled_data)

                # Agrupar agents por cluster
                clusters = {}
                for i, label in enumerate(cluster_labels):
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(agent_names[i])

                return {
                    "performance_clusters": clusters,
                    "cluster_centers": kmeans.cluster_centers_.tolist(),
                    "n_clusters": n_clusters,
                }
            else:
                return {"single_cluster": "All agents in one performance group"}

        except Exception as e:
            return {"clustering_error": str(e)}

    def _analyze_behavioral_patterns(
        self, agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analisa padrões comportamentais dos agents"""
        behavioral_patterns = {}

        for agent in agents:
            agent_id = agent["id"]
            metrics = agent.get("metrics", {})
            category_scores = agent.get("category_scores", {})

            # Análise de consistência entre categorias
            category_values = list(category_scores.values())
            if category_values:
                std_dev = np.std(category_values)
                mean_score = np.mean(category_values)

                behavioral_patterns[agent_id] = {
                    "score_consistency": (
                        "High" if std_dev < 5 else "Medium" if std_dev < 10 else "Low"
                    ),
                    "category_strengths": self._identify_category_strengths(
                        category_scores
                    ),
                    "category_weaknesses": self._identify_category_weaknesses(
                        category_scores
                    ),
                    "overall_performance_profile": self._profile_performance(metrics),
                }

        return behavioral_patterns

    def _analyze_metric_correlations(
        self, agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analisa correlações entre métricas"""
        if len(agents) < 3:
            return {
                "insufficient_data": "Need at least 3 agents for correlation analysis"
            }

        # Coletar dados de métricas
        accuracy_scores = []
        latency_scores = []
        token_usage = []
        consistency_scores = []

        for agent in agents:
            metrics = agent.get("metrics", {})
            accuracy_scores.append(metrics.get("accuracy", 0))
            latency_scores.append(metrics.get("latency_avg", 0))
            token_usage.append(metrics.get("tokens_avg", 0))
            consistency_scores.append(metrics.get("consistency", 0))

        # Calcular correlações
        try:
            corr_accuracy_latency = np.corrcoef(accuracy_scores, latency_scores)[0, 1]
            corr_accuracy_tokens = np.corrcoef(accuracy_scores, token_usage)[0, 1]
            corr_latency_tokens = np.corrcoef(latency_scores, token_usage)[0, 1]

            return {
                "accuracy_vs_latency_correlation": float(corr_accuracy_latency),
                "accuracy_vs_tokens_correlation": float(corr_accuracy_tokens),
                "latency_vs_tokens_correlation": float(corr_latency_tokens),
                "correlation_interpretation": self._interpret_correlations(
                    {
                        "acc_lat": corr_accuracy_latency,
                        "acc_tok": corr_accuracy_tokens,
                        "lat_tok": corr_latency_tokens,
                    }
                ),
            }
        except Exception as e:
            return {"correlation_error": str(e)}

    def _detect_anomalies(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detecta anomalias nos resultados"""
        anomalies = []

        # Calcular estatísticas básicas para detecção de outliers
        metrics_collection = {
            "accuracy": [],
            "latency": [],
            "tokens": [],
            "consistency": [],
        }

        for agent in agents:
            metrics = agent.get("metrics", {})
            metrics_collection["accuracy"].append(metrics.get("accuracy", 0))
            metrics_collection["latency"].append(metrics.get("latency_avg", 0))
            metrics_collection["tokens"].append(metrics.get("tokens_avg", 0))
            metrics_collection["consistency"].append(metrics.get("consistency", 0))

        # Detectar outliers usando desvio padrão
        for metric_name, values in metrics_collection.items():
            if len(values) >= 3:  # Precisamos de dados suficientes
                mean_val = np.mean(values)
                std_val = np.std(values)

                # Definir limite para outliers (2 desvios padrão)
                lower_bound = mean_val - 2 * std_val
                upper_bound = mean_val + 2 * std_val

                # Verificar cada agente
                for agent in agents:
                    agent_id = agent["id"]
                    agent_metric = agent["metrics"].get(
                        (
                            "accuracy"
                            if metric_name == "accuracy"
                            else (
                                "latency_avg"
                                if metric_name == "latency"
                                else (
                                    "tokens_avg"
                                    if metric_name == "tokens"
                                    else "consistency"
                                )
                            )
                        ),
                        0,
                    )

                    if agent_metric < lower_bound or agent_metric > upper_bound:
                        anomalies.append(
                            {
                                "agent_id": agent_id,
                                "metric": metric_name,
                                "value": agent_metric,
                                "mean": float(mean_val),
                                "std_dev": float(std_val),
                                "type": (
                                    "low_outlier"
                                    if agent_metric < lower_bound
                                    else "high_outlier"
                                ),
                            }
                        )

        return {"detected_anomalies": anomalies}

    def _generate_recommendations(self, agents: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []

        # Recomendações baseadas em performance individual
        for agent in agents:
            agent_id = agent["id"]
            metrics = agent.get("metrics", {})
            accuracy = metrics.get("accuracy", 0)
            latency = metrics.get("latency_avg", 0)
            tokens = metrics.get("tokens_avg", 0)
            consistency = metrics.get("consistency", 0)

            # Recomendações específicas por métrica
            if accuracy < 75:
                recommendations.append(
                    f"Considerar fine-tuning para {agent_id} para melhorar precisão"
                )

            if latency > 5.0:
                recommendations.append(f"Otimizar tempo de resposta para {agent_id}")

            if tokens > 2000:
                recommendations.append(
                    f"Avaliar eficiência de token usage para {agent_id}"
                )

            if consistency < 4.0:
                recommendations.append(
                    f"Melhorar consistência de respostas para {agent_id}"
                )

        # Recomendações comparativas
        if len(agents) > 1:
            accuracy_scores = {
                agent["id"]: agent["metrics"].get("accuracy", 0) for agent in agents
            }
            best_accuracy_agent = max(accuracy_scores, key=accuracy_scores.get)
            worst_accuracy_agent = min(accuracy_scores, key=accuracy_scores.get)

            if (
                accuracy_scores[best_accuracy_agent]
                - accuracy_scores[worst_accuracy_agent]
                > 10
            ):
                recommendations.append(
                    f"Comparar configurações de {best_accuracy_agent} com {worst_accuracy_agent} para identificar fatores de sucesso"
                )

        # Recomendações gerais
        recommendations.append(
            "Considerar execução de benchmarks adicionais para validação estatística"
        )
        recommendations.append("Documentar configurações ótimas identificadas")
        recommendations.append("Monitorar tendências de performance ao longo do tempo")

        return list(set(recommendations))  # Remover duplicatas

    def _identify_category_strengths(
        self, category_scores: Dict[str, float]
    ) -> List[str]:
        """Identifica forças por categoria"""
        if not category_scores:
            return []

        mean_score = np.mean(list(category_scores.values()))
        strengths = [
            cat for cat, score in category_scores.items() if score > mean_score + 5
        ]
        return strengths

    def _identify_category_weaknesses(
        self, category_scores: Dict[str, float]
    ) -> List[str]:
        """Identifica fraquezas por categoria"""
        if not category_scores:
            return []

        mean_score = np.mean(list(category_scores.values()))
        weaknesses = [
            cat for cat, score in category_scores.items() if score < mean_score - 5
        ]
        return weaknesses

    def _profile_performance(self, metrics: Dict[str, Any]) -> str:
        """Cria perfil de performance"""
        accuracy = metrics.get("accuracy", 0)
        latency = metrics.get("latency_avg", 0)
        consistency = metrics.get("consistency", 0)

        if accuracy >= 85 and latency <= 3 and consistency >= 4:
            return "High Performance"
        elif accuracy >= 75 and latency <= 5 and consistency >= 3:
            return "Balanced Performance"
        else:
            return "Needs Improvement"

    def _interpret_correlations(self, correlations: Dict[str, float]) -> Dict[str, str]:
        """Interpreta correlações"""
        interpretation = {}

        for key, corr in correlations.items():
            if abs(corr) > 0.7:
                interpretation[key] = "Strong correlation"
            elif abs(corr) > 0.3:
                interpretation[key] = "Moderate correlation"
            else:
                interpretation[key] = "Weak correlation"

        return interpretation


# Instância global
data_deduction_engine = DataDeductionEngine()
