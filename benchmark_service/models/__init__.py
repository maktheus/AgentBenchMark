"""
Modelos de dados para o serviço de benchmark
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class BenchmarkRequest(BaseModel):
    """Modelo para requisição de benchmark"""

    agents: List[str]
    benchmark: str
    config: Optional[Dict[str, Any]] = None


class AgentResult(BaseModel):
    """Modelo para resultado de um agent"""

    id: str
    metrics: Dict[str, Any]
    category_scores: Dict[str, Any]


class BenchmarkResult(BaseModel):
    """Modelo para resultado completo de um benchmark"""

    run_id: str
    benchmark: str
    agents: List[AgentResult]
    summary: Dict[str, Any]


class BenchmarkRun(BaseModel):
    """Modelo para execução de um benchmark"""

    run_id: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    agents: List[str]
    benchmark: str
    config: Optional[Dict[str, Any]] = None
    results_url: Optional[str] = None


class BenchmarkInfo(BaseModel):
    """Modelo para informações de um benchmark disponível"""

    id: str
    name: str
    description: str
    categories: List[str]
    question_count: int
