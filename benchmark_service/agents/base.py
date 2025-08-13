"""
Interface base para todos os agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class AgentInterface(ABC):
    """Interface padrão para agents de IA"""

    @abstractmethod
    async def query(
        self, prompt: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Envia uma consulta ao agent"""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o agent"""
        pass
