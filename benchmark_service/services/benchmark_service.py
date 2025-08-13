"""
Serviço principal de benchmark
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json


class BenchmarkService:
    """Serviço principal para gerenciar benchmarks"""

    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "benchmark_db"),
            "user": os.getenv("DB_USER", "benchmark_user"),
            "password": os.getenv("DB_PASSWORD", "benchmark_password"),
            "port": os.getenv("DB_PORT", "5432"),
        }

    def _get_db_connection(self):
        """Obtém conexão com o banco de dados"""
        return psycopg2.connect(**self.db_config)

    async def start_benchmark(
        self, agents: List[str], benchmark: str, config: Dict[str, Any] = None
    ) -> str:
        """Inicia um novo benchmark"""
        run_id = str(uuid.uuid4())

        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Convert Python objects to JSON strings for database insertion
            agents_json = json.dumps(agents) if agents else None
            config_json = json.dumps(config) if config else None

            cursor.execute(
                """
                INSERT INTO benchmarks (run_id, status, agents, benchmark_type,
                config, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (run_id, "queued", agents_json, benchmark, config_json, datetime.now()),
            )

            conn.commit()
            cursor.close()
            conn.close()

            return run_id
        except Exception as e:
            print(f"Erro ao iniciar benchmark: {e}")
            raise e

    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de um benchmark"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """
                SELECT * FROM benchmarks WHERE run_id = %s
            """,
                (run_id,),
            )

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                # Convert JSON strings back to Python objects
                result_dict = dict(result)
                if result_dict.get("agents"):
                    # Check if it's already a Python object or a JSON string
                    if isinstance(result_dict["agents"], str):
                        result_dict["agents"] = json.loads(result_dict["agents"])
                if result_dict.get("config"):
                    # Check if it's already a Python object or a JSON string
                    if isinstance(result_dict["config"], str):
                        result_dict["config"] = json.loads(result_dict["config"])

                # Map database fields to expected API fields
                result_dict["benchmark"] = result_dict.pop("benchmark_type", "")
                if result_dict.get("status") == "completed":
                    result_dict["results_url"] = f"/api/benchmark/results/{run_id}"

                return result_dict
            return None
        except Exception as e:
            print(f"Erro ao obter status do benchmark: {e}")
            return None

    async def start_processing(self, run_id: str):
        """Marca o benchmark como em processamento"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE benchmarks
                SET status = %s, started_at = %s, progress = %s
                WHERE run_id = %s
            """,
                ("processing", datetime.now(), 0.0, run_id),
            )

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao iniciar processamento do benchmark: {e}")
            raise e

    async def update_progress(self, run_id: str, progress: float):
        """Atualiza o progresso do benchmark"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE benchmarks
                SET progress = %s
                WHERE run_id = %s
            """,
                (min(1.0, max(0.0, progress)), run_id),
            )

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao atualizar progresso do benchmark: {e}")
            raise e

    async def complete_benchmark(self, run_id: str, results: Dict[str, Any]):
        """Completa o benchmark com resultados"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Atualizar status do benchmark
            cursor.execute(
                """
                UPDATE benchmarks
                SET status = %s, completed_at = %s, progress = %s
                WHERE run_id = %s
            """,
                ("completed", datetime.now(), 1.0, run_id),
            )

            # Inserir resultados
            if "agents" in results:
                for agent_data in results["agents"]:
                    # Convert Python objects to JSON strings
                    metrics_json = json.dumps(agent_data.get("metrics", {}))
                    category_scores_json = json.dumps(
                        agent_data.get("category_scores", {})
                    )

                    cursor.execute(
                        """
                        INSERT INTO benchmark_results (run_id, agent_id, metrics,
                        category_scores)
                        VALUES (%s, %s, %s, %s)
                    """,
                        (run_id, agent_data["id"], metrics_json, category_scores_json),
                    )

            # Inserir análise e deduções se existirem
            if "analysis" in results or "deductions" in results:
                # Convert Python objects to JSON strings
                analysis_json = json.dumps(results.get("analysis", {}))
                deductions_json = json.dumps(results.get("deductions", {}))

                cursor.execute(
                    """
                    INSERT INTO analytics_history (run_id, analysis, deductions)
                    VALUES (%s, %s, %s)
                """,
                    (run_id, analysis_json, deductions_json),
                )

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao completar benchmark: {e}")
            raise e

    async def fail_benchmark(self, run_id: str, error: str):
        """Marca o benchmark como falho"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE benchmarks
                SET status = %s, completed_at = %s
                WHERE run_id = %s
            """,
                ("failed", datetime.now(), run_id),
            )

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao marcar benchmark como falho: {e}")
            raise e
