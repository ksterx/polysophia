import asyncio
import json
import uuid
from typing import Any, Literal

import graphviz
import numpy as np
import requests
import websockets

# import websockets
from pydantic import BaseModel, Field

from polysophia import logger

from .data import DataPacket
from .memory import Memory


class Processor(BaseModel):
    name: str = Field(..., description="Name of the processor")

    def __call__(self, *args, **kwargs):
        pass


class NodeCallback(BaseModel):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_start(self):
        pass

    def on_stop(self):
        pass


class Node(BaseModel):
    id: uuid.UUID = Field(uuid.uuid4(), description="Unique identifier of the node")
    name: str = Field(..., description="Name of the node")
    callbacks: dict[str, NodeCallback] = Field({}, description="Callbacks of the node")
    processor: Processor | None = Field(None, description="Processor of the node")
    status: Literal["up", "down"] = Field("down", description="Status of the node")

    def __repr__(self) -> str:
        return f"Node('{self.name}')"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(self.id)

    def up(self):
        pass

    def down(self):
        pass

    def on_start(self):
        logger.info(f"{self.name} started")
        for callback in self.callbacks:
            callback.on_start()

    def on_connect(self):
        logger.info(f"{self.name} connected")
        for callback in self.callbacks:
            callback.on_connect()

    def on_disconnect(self):
        logger.info(f"{self.name} disconnected")
        for callback in self.callbacks:
            callback.on_disconnect()


class Publisher(Node):
    processor: Processor
    memory: Memory | None = Field(None, description="Memory of the publisher")
    memory_kwargs: dict[str, Any] | None = Field(None, description="Memory kwargs")

    def publish(self, **kwargs):
        while True:
            if self.memory:
                inputs = self.memory.read(self.name)
                self.processor(**inputs, **kwargs)
            else:
                self.processor(**kwargs)


class Subscriber(Node):
    def __init__(self, processor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = processor

    async def subscribe(self):
        async with websockets.connect(self.address) as websocket:
            while True:
                data = await websocket.recv()
                self.processor(data)


class CallableNode(Node):
    def __init__(self, processor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = processor

    def __call__(self, inputs: dict[str, Any]):
        self.processor(**inputs)


class Server(CallableNode):
    async def respond(self, data: DataPacket) -> None:
        x = self.processor(data)
        requests.post(self.address, json=json.dumps(x))


class Client(CallableNode):
    async def request(self):
        data = requests.get(self.address)
        self.processor(data)

    async def post(self, data: DataPacket):
        requests.post(self.address, json=json.dumps(data))


class Graph:
    def __init__(self):
        self.nodes = set()
        self.connections = np.array([])

    def __repr__(self):
        return f"Graph({self.node_list})"

    def __str__(self):
        return self.__repr__()

    def add(self, node: Node) -> None:
        self.nodes.add(node)
        self._update_connection(1)

    def remove(self, node: int | Node) -> None:
        if isinstance(node, int):
            self.nodes.remove(self.node_list[node])
        elif isinstance(node, Node):
            self.nodes.remove(node)
        else:
            raise TypeError("node should be Node or int")

        logger.info(f"{node} removed")

    def connect(self, node1: Node, node2: Node) -> None:
        idx_1, idx_2 = self.node_list.index(node1), self.node_list.index(node2)
        if self.connections[idx_1, idx_2] == 0:
            self.connections[idx_1, idx_2] = 1
        elif self.connections[idx_1, idx_2] == 1:
            logger.warning(f"{node1} and {node2} are already connected")
        logger.info(f"{node1} -> {node2}")

    def disconnect(self, node1: Node, node2: Node) -> None:
        idx_1, idx_2 = self.node_list.index(node1), self.node_list.index(node2)
        if self.connections[idx_1, idx_2] == 1:
            self.connections[idx_1, idx_2] = 0
        elif self.connections[idx_2, idx_1] == 0:
            logger.warning(f"{node1} and {node2} are not connected")
        logger.info(f"{node1} -/-> {node2}")

    def run(self):
        for node in self.nodes:
            node.on_connect()
            node.on_disconnect()

    def _update_connection(self, num_nodes: int) -> np.ndarray:
        old_conn = self.connections.copy()
        if len(self.connections.shape) == 1:
            n = 0
        else:
            n = self.connections.shape[0]
        A = np.zeros((n + num_nodes, n + num_nodes))
        A[:n, :n] = old_conn
        self.connections = A

        for i in range(n, n + num_nodes):
            self.connections[i, i] = 1

    @property
    def node_list(self) -> list[Node]:
        return list(self.nodes)

    def print_nodes(self) -> None:
        print("=" * 40 + " Nodes " + "=" * 40)
        for i, node in enumerate(self.nodes):
            print(f"{i}: {node}")
        print("=" * 87)

    def visualize(
        self,
        filename: str = "graph",
        directory: str | None = None,
        view: bool = False,
        **kwargs,
    ) -> None:
        g = graphviz.Digraph()
        for node in self.node_list:
            g.node(node.name)
        for i in range(self.connections.shape[0]):
            for j in range(self.connections.shape[1]):
                if self.connections[i, j] == 1 and i != j:
                    g.edge(self.node_list[i].name, self.node_list[j].name)
        g.render(filename, directory, format="png", cleanup=True, view=view, **kwargs)
