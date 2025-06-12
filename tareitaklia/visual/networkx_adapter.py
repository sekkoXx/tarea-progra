
import networkx as nx
from model.graph import Graph, Vertex, Edge # Asegúrate de que estos imports sean correctos según tu implementación

class NetworkXAdapter:
    def __init__(self, custom_graph: Graph):
        self.custom_graph = custom_graph
        self.nx_graph = self._convert_to_networkx()

    def _convert_to_networkx(self):
        nx_graph = nx.DiGraph() # O nx.Graph() si tus aristas son bidireccionales por defecto

        # Añadir nodos
        for vertex_id, vertex_obj in self.custom_graph.vertices.items():
            nx_graph.add_node(vertex_id, role=vertex_obj.role)

        # Añadir aristas
        for edge in self.custom_graph.edges:
            nx_graph.add_edge(edge.source.id, edge.destination.id, weight=edge.weight)
            # Si las aristas son bidireccionales, añade la arista en sentido inverso también
            # nx_graph.add_edge(edge.destination.id, edge.source.id, weight=edge.weight)
        return nx_graph

    def get_networkx_graph(self):
        return self.nx_graph
    

