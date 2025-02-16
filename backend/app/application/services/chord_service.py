from abc import ABC, abstractmethod
from app.domain.distribute.chord import ChordNode

class IChordService(ABC):
    """Interfaz para abstraer la lógica de Chord."""

    @abstractmethod
    def get_node(self) -> ChordNode:
        """Retorna el nodo Chord actual."""
        pass

    @abstractmethod
    def join_network(self, known_node_ip: str = None) -> None:
        """Permite unirse a la red, usando (si se indica) la IP de un nodo conocido."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Inicia los servicios de Chord (hilos, servidor, multicast, etc.)."""
        pass
