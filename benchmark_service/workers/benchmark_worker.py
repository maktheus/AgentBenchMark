"""
Worker para processamento assíncrono de benchmarks
"""

import asyncio
import json
import os
from typing import Dict, Any
from datetime import datetime
from ..agents.openai_adapter import OpenAIAgentAdapter, OpenAIConfig
from ..agents.anthropic_adapter import AnthropicAgentAdapter, AnthropicConfig
from ..agents.local_adapter import LocalAgentAdapter, LocalAgentConfig
from ..services.benchmark_service import BenchmarkService
from ..analytics.benchmark_analytics import benchmark_analytics
from ..analytics.data_deduction import data_deduction_engine
from ..evaluators.benchmark_evaluator import benchmark_evaluator


class BenchmarkWorker:
    """Worker para executar benchmarks de forma assíncrona"""

    def __init__(self):
        self.benchmark_service = BenchmarkService()

    async def process_benchmark(self, run_id: str, benchmark_config: Dict[str, Any]):
        """Processa um benchmark específico"""
        try:
            # Carregar dataset
            dataset_path = (
                f"benchmark_service/datasets/{benchmark_config['benchmark']}.json"
            )
            if not os.path.exists(dataset_path):
                raise FileNotFoundError(
                    f"Dataset {benchmark_config['benchmark']} not found"
                )

            with open(dataset_path, "r") as f:
                dataset = json.load(f)

            # Inicializar agents
            agents = []
            for agent_name in benchmark_config["agents"]:
                agent = await self._create_agent(agent_name, benchmark_config)
                if agent:
                    agents.append((agent_name, agent))

            # Processar cada questão do dataset
            results = []
            for question in dataset["data"]:
                question_results = {
                    "question_id": question["id"],
                    "agent_responses": [],
                }

                # Enviar para cada agent
                for agent_name, agent in agents:
                    try:
                        response = await agent.query(question["question"])
                        question_results["agent_responses"].append(
                            {
                                "agent": agent_name,
                                "response": response,
                                "correct": (
                                    response.get("response", "").strip()
                                    == question["answer"]
                                    if "response" in response
                                    else False
                                ),
                            }
                        )
                    except Exception as e:
                        question_results["agent_responses"].append(
                            {"agent": agent_name, "error": str(e), "correct": False}
                        )

                results.append(question_results)

            # Avaliar resultados
            evaluated_results = benchmark_evaluator.evaluate_results(results)

            # Processar resultados para o formato esperado
            processed_results = self._process_evaluated_results(
                evaluated_results, benchmark_config["benchmark"]
            )

            # Analisar resultados com analytics
            analysis = benchmark_analytics.analyze_benchmark_results(processed_results)

            # Deduzir padrões com o motor de dedução
            deductions = data_deduction_engine.deduct_patterns(processed_results)

            # Adicionar análise e deduções aos resultados
            processed_results["analysis"] = analysis
            processed_results["deductions"] = deductions

            # Atualizar status do benchmark
            await self.benchmark_service.complete_benchmark(run_id, processed_results)

        except Exception as e:
            await self.benchmark_service.fail_benchmark(run_id, str(e))
            raise e

    async def _create_agent(self, agent_name: str, benchmark_config: Dict[str, Any]):
        """Cria um agent com base no nome e configuração"""
        try:
            if agent_name.startswith("gpt-"):
                config = OpenAIConfig(
                    api_key=os.getenv("OPENAI_API_KEY", "test-key"),
                    model=agent_name,
                    temperature=benchmark_config.get("config", {}).get(
                        "temperature", 0.7
                    ),
                    max_tokens=benchmark_config.get("config", {}).get(
                        "max_tokens", 1024
                    ),
                )
                return OpenAIAgentAdapter(config)

            elif agent_name.startswith("claude-"):
                config = AnthropicConfig(
                    api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
                    model=agent_name,
                    temperature=benchmark_config.get("config", {}).get(
                        "temperature", 0.7
                    ),
                    max_tokens=benchmark_config.get("config", {}).get(
                        "max_tokens", 1024
                    ),
                )
                return AnthropicAgentAdapter(config)

            elif agent_name == "local":
                config = LocalAgentConfig(
                    endpoint=os.getenv(
                        "LOCAL_AGENT_ENDPOINT", "http://localhost:8001/chat"
                    ),
                    model="local-model",
                    timeout=30.0,
                )
                return LocalAgentAdapter(config)

            else:
                # Tentar criar um agent local com configuração customizada
                if agent_name.startswith("local:"):
                    endpoint = agent_name.split(":", 1)[1]
                    config = LocalAgentConfig(
                        endpoint=endpoint, model="custom-local-model", timeout=30.0
                    )
                    return LocalAgentAdapter(config)

                # Agent não suportado
                return None

        except Exception as e:
            print(f"Erro ao criar agent {agent_name}: {e}")
            return None

    def _process_evaluated_results(
        self, evaluated_results: Dict[str, Any], benchmark_id: str
    ) -> Dict[str, Any]:
        """Processa resultados avaliados para o formato esperado"""
        agents_data = []

        for agent_name, agent_data in evaluated_results.items():
            metrics = agent_data.get("metrics", {})

            # Criar scores por categoria (simplificado)
            category_scores = {
                "mathematics": metrics.get("accuracy", 0) * 0.9,
                "logical_reasoning": metrics.get("accuracy", 0) * 0.85,
            }

            agents_data.append(
                {
                    "id": agent_name,
                    "metrics": metrics,
                    "category_scores": category_scores,
                }
            )

        # Determinar top performer
        if agents_data:
            top_performer = max(
                agents_data, key=lambda x: x["metrics"].get("accuracy", 0)
            )["id"]
        else:
            top_performer = "none"

        return {
            "benchmark": benchmark_id,
            "agents": agents_data,
            "summary": {
                "top_performer": top_performer,
                "critical_observations": [
                    "Análise de performance completa disponível",
                    "Insights avançados gerados automaticamente",
                ],
            },
        }


# Instância global do worker
benchmark_worker = BenchmarkWorker()
