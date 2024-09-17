from polysophia import Graph, Node

graph = Graph()
node1 = Node(name="node1")
node2 = Node(name="node2")

graph.add(node1)
graph.add(node2)
graph.connect(node1, node2)
graph.show_nodes()
print(graph.connections)
print(graph.node_list)
print(graph)
