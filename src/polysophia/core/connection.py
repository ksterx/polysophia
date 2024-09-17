import asyncio
import json
import uuid
from typing import Any, Literal

import numpy as np
import requests

# import websockets
from pydantic import BaseModel, Field

from polysophia import logger

from .data import DataPacket
from .memory import Memory


class Processor(BaseModel):
    name: str = Field(..., description="Name of the processor")

    def __call__(self, *args, **kwargs):
        pass


class Node(BaseModel):
    id: uuid.UUID = Field(uuid.uuid4())
    name: str = Field(..., description="Name of the node")
    callbacks: dict[str, Any | None] = Field({}, description="Callbacks of the node")
    processor: Processor | None = Field(None, description="Processor of the node")
    status: Literal["up", "down"] = Field("down", description="Status of the node")

    def __repr__(self) -> str:
        return f"Node({self.name})"

    def __hash__(self) -> int:
        return hash(self.id)

    def up(self):
        pass

    def down(self):
        pass

    def on_start(self):
        logger.info(f"{self.name} started")

    def on_connect(self):
        logger.info(f"{self.name} connected")

    def on_disconnect(self):
        logger.info(f"{self.name} disconnected")


class TopicNode(Node):
    topic: str = Field(..., description="Topic of the node")


class Publisher(TopicNode):
    def __init__(self, processor, memory: Memory | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = processor
        self.memory = memory

    def publish(self):
        while True:
            inputs = self.memory.read(self.topic)
            self.processor(**inputs)


class Subscriber(TopicNode):
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

    def add(self, node: Node):
        self.nodes.add(node)
        self._add(1)

    def remove(self, node: int | Node) -> None:
        if isinstance(node, int):
            self.nodes.remove(self.node_list[node])
        elif isinstance(node, Node):
            self.nodes.remove(node)
        else:
            raise TypeError("node should be Node or int")

        logger.info(f"Node ({node.name}) removed")


    def connect(self, node1: Node, node2: Node):
        self.connections[self.node_list.index(node1), self.node_list.index(node2)] = 1
        logger.info(f"{node1.name} -> {node2.name}")

    def disconnect(self, node1: Node, node2: Node):
        self.connections[self.node_list.index(node1), self.node_list.index(node2)] = 0
        logger.info(f"{node1.name} -/-> {node2.name}")

    def run(self):
        for node in self.nodes:
            node.on_connect()
            node.on_disconnect()


    def _add(self, num_nodes: int) -> np.ndarray:
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
    def node_list(self):
        return list(self.nodes)

    def show_nodes(self):
        for i, node in enumerate(self.node_list):
            print(f"{i}: {node}")
