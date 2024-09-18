from polysophia import Graph, Node
from polysophia.sensors.camera import Camera, CameraPublisher

graph = Graph()
node1 = Node(name="node1")
node2 = Node(name="node2")
cam = CameraPublisher()

cam.publish(view=True)

# graph.add(node1)
# graph.add(node2)
# graph.connect(node1, node2)
# graph.print_nodes()
# print(graph.connections)
# print(graph.node_list)
# print(graph)
# graph.visualize()
# graph.disconnect(node1, node2)
# graph.remove(node1)
