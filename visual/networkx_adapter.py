import networkx as nx
from model.edge import Edge

class NetworkXAdapter:
    def __init__(self, custom_graph):
        self.custom_graph = custom_graph
        self.nx_graph = self._convert_to_networkx()

    def _convert_to_networkx(self):
        G = nx.Graph()
        for v in self.custom_graph.vertices():
            v_id = v.element()['id']
            role = "almacenamiento" if v.is_warehouse else "recarga" if v.is_recharge else "cliente"
            G.add_node(v_id, role=role)
        for e in self.custom_graph.edges():
            u_id = e.endpoints()[0].element()['id']
            v_id = e.endpoints()[1].element()['id']
            G.add_edge(u_id, v_id, weight=e.cost())
        return G

    def get_networkx_graph(self):
        return self.nx_graph
