import logging
from app.domain.distribute.chord import ChordNode, ChordNodeReference
from app.application.services.chord_service import IChordService


class ChordService(IChordService):
    def __init__(self, ip: str, port: int = 8001):
        self.node = ChordNode(ip, port)

    def join_network(self, known_node_ip: str = None) -> None:
        if known_node_ip:
            known_node = ChordNodeReference(known_node_ip, self.node.port)
            self.node.join(known_node)
        else:
            self.node.join(None)

    def start(self) -> None:
        logging.info("Iniciando servicios de Chord desde ChordService...")
        self.node.start_services()

    def get_node(self) -> ChordNode:
        return self.node
