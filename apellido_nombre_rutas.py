from vertex import Vertex
from edge import Edge
from graph import Graph
from AVL import *

# Parte 1: Algoritmo de Ruta con Recarga Inteligente

class RouteManager:
    def __init__(self, graph=Graph()):
        self.graph = graph
    
    def find_nearest_recharge(self, vertex):
        """Encuentra la estación de recarga más cercana entre los vecinos."""
        for neighbor in self.graph.neighbors(vertex):
            if neighbor.element()['estacion']:
                return neighbor
        return None

    def find_route_with_recharge(self, origin_id, destination_id, battery_limit=50):
        # Primero se obtienen los vértices de origen y destino
        for vertex in self.graph.vertices():
            if vertex.element()['id'] == origin_id:
                origin = vertex
            if vertex.element()['id'] == destination_id:
                destination = vertex
        if not origin or not destination:
            print("Origen o destino no encontrado.")
            return None
        
        # BFS modificado para considerar recargas
        visitados = set()
        cola = []
        bateria_actual = battery_limit
        costo_total = 0
        ruta = []
        recargas = []
        segmentos = []
        visitados.add(origin)
        cola.append(origin)

        print(f"Buscando ruta desde {origin.element()['id']} hasta {destination.element()['id']} con batería de {battery_limit}.")

        while cola:
            actual = cola.pop(0)
            ruta.append(actual.element())
            if actual == destination:
                return {
                    'ruta': ruta,
                    'costo_total': costo_total,
                    'recargas': recargas,
                    'segmentos': segmentos
                }

            for vecino in self.graph.neighbors(actual):
                if vecino not in visitados:
                    print(f"Visitando vecino: {vecino.element()['id']}")
                    arista = self.graph.get_edge(actual, vecino)
                    if arista:
                        costo_arista = arista.element()
                        if bateria_actual >= costo_arista:
                            bateria_actual -= costo_arista
                            costo_total += costo_arista
                            visitados.add(vecino)
                            cola.append(vecino)
                        else:
                            # Si no hay suficiente batería, buscar recarga
                            recarga = self.find_nearest_recharge(actual)
                            if recarga and recarga not in recargas:
                                recargas.append(recarga.element())
                                bateria_actual = battery_limit

        return None


if __name__ == "__main__":
    # Grafo de ejemplo
    graph = Graph()

    # Agregar vértices
    vertices_creados = []
    for i in range(100):
        v = graph.insert_vertex({"id":i, 'estacion': False})
        vertices_creados.append(v)
    
    # Agregar aristas
    for i in range(99):
        graph.insert_edge(vertices_creados[i], vertices_creados[i+1], 10)  # Arista con costo 10
    
    print("Grafo creado con 100 vértices y 99 aristas.")

    rutador = RouteManager(graph)
    print("Buscando ruta con recarga entre 0 y 20...")
    resultado = rutador.find_route_with_recharge(0, 5, battery_limit=50)
    if resultado:
        print("Ruta encontrada:")
        print("Ruta:", resultado['ruta'])
        print("Costo total:", resultado['costo_total'])
        print("Recargas:", resultado['recargas'])
        print("Segmentos:", resultado['segmentos'])
    else:
        print("No se encontró una ruta válida.")

