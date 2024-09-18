if __name__ == "__main__":
    from polysophia.core.connection import Graph, Node, Processor, Publisher, Subscriber

    graph = Graph()

    class PrintProcessor(Processor):
        def __call__(self, text: str):
            print(f"Processor ({self.name}): {text}")

    pub = Publisher(name="publisher", topic="text")

    sub = Subscriber(name="subscriber", topic="text")

    graph.add(pub)
    graph.add(sub)
    graph.connect(pub, sub, via="http://127.0.0.1:4567")

    graph.run()
