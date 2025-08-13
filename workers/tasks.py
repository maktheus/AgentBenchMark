"""
Tarefas do Celery para execução de benchmarks
"""

from celery import current_task
from .celery_app import celery_app
import asyncio
from typing import Dict, Any
import time


@celery_app.task(bind=True)
def run_benchmark(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa um benchmark de forma assíncrona
    """
    try:
        # Simula execução de benchmark
        task_id = self.request.id

        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting benchmark..."},
        )

        # Simula processamento
        for i in range(0, 101, 10):
            time.sleep(0.5)  # Simula trabalho
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": i,
                    "total": 100,
                    "status": f"Processing... {i}% complete",
                },
            )

        # Resultado final
        result = {
            "task_id": task_id,
            "status": "completed",
            "config": config,
            "metrics": {
                "execution_time": 5.0,
                "success_rate": 0.95,
                "avg_response_time": 1.2,
                "total_requests": 100,
                "failed_requests": 5,
            },
        }

        return result

    except Exception as e:
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task
def health_check() -> Dict[str, str]:
    """
    Health check para workers
    """
    return {"status": "healthy", "timestamp": time.time()}
