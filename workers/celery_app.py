"""
Configuração do Celery para workers
"""

from celery import Celery
import os

# Configuração do Celery
celery_app = Celery(
    "benchmark",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["workers.tasks"],
)

# Configurações
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "workers.tasks.run_benchmark": "benchmark_queue",
    },
)

if __name__ == "__main__":
    celery_app.start()
