
from model.graph import Graph, Vertex, Edge
from collections import deque
import heapq # Para una posible implementación de Dijkstra o A* si se permite más adelante, o para priorizar nodos de recarga

class Simulation:
    def __init__(self):
        self.graph = None
        self.orders = {}
        self.clients = {}
        self.order_counter = 0

    def initialize_simulation(self, n_nodes, m_edges, n_orders):
        # Esta función generaría el grafo, asignaría roles, etc.
        # (El contenido real de la inicialización de la simulación va aquí)
        self.graph = Graph()
        # Ejemplo básico de inicialización de grafo (esto debería ser más complejo)
        for i in range(n_nodes):
            role = "cliente"
            if i < n_nodes * 0.2:
                role = "almacenamiento"
            elif n_nodes * 0.2 <= i < n_nodes * 0.4:
                role = "recarga"
            self.graph.add_vertex(f"Node_{i}", role)

        # Añadir algunas aristas para que sea un grafo conectado (ejemplo muy básico)
        for i in range(m_edges):
            u = f"Node_{i % n_nodes}"
            v = f"Node_{(i + 1) % n_nodes}"
            weight = (i % 10) + 1 # Ejemplo de peso
            self.graph.add_edge(u, v, weight)
            # Si el grafo es no dirigido, añade la arista en ambos sentidos
            self.graph.add_edge(v, u, weight) # Asumiendo grafo no dirigido para simplificar el ejemplo

        # (Resto de la inicialización, como clientes y órdenes)
        st.success(f"Simulation initialized with {n_nodes} nodes, {m_edges} edges, {n_orders} orders.")


    def find_route_with_recharge(self, start_node_id: str, end_node_id: str, max_autonomy: int):
        if start_node_id not in self.graph.vertices or end_node_id not in self.graph.vertices:
            return {"path": [], "cost": -1}

       
        queue = deque([(start_node_id, [start_node_id], 0)])

        pq = [(0, start_node_id, max_autonomy, [start_node_id])]

        # Para almacenar el costo mínimo para llegar a un nodo con una cierta cantidad de energía
        min_cost_to_reach = {} # Key: (node_id, energy_remaining), Value: min_total_cost

        min_cost_to_reach[(start_node_id, max_autonomy)] = 0

        best_path_found = None
        min_total_cost = float('inf')

        while pq:
            current_total_cost, current_node_id, current_energy, current_path = heapq.heappop(pq)

            if current_node_id == end_node_id:
                if current_total_cost < min_total_cost:
                    min_total_cost = current_total_cost
                    best_path_found = current_path
                continue # Continuar buscando caminos potencialmente más cortos

            # Evitar explorar caminos peores si ya encontramos uno mejor para este estado
            if (current_node_id, current_energy) in min_cost_to_reach and \
               current_total_cost > min_cost_to_reach[(current_node_id, current_energy)]:
                continue

            # Considerar recarga si el nodo actual es una estación de recarga
            if self.graph.vertices[current_node_id].role == "recarga":
                # Recargar completamente el dron sin costo adicional (asumido por ahora)
                recharged_energy = max_autonomy
                if (current_node_id, recharged_energy) not in min_cost_to_reach or \
                   current_total_cost < min_cost_to_reach[(current_node_id, recharged_energy)]:
                    min_cost_to_reach[(current_node_id, recharged_energy)] = current_total_cost
                    heapq.heappush(pq, (current_total_cost, current_node_id, recharged_energy, current_path))


            for edge in self.graph.get_edges_from_vertex(current_node_id):
                next_node_id = edge.destination.id
                edge_weight = edge.weight

                new_energy = current_energy - edge_weight
                new_total_cost = current_total_cost + edge_weight
                new_path = current_path + [next_node_id]

                # Si la energía es suficiente para el siguiente tramo
                if new_energy >= 0:
                    if (next_node_id, new_energy) not in min_cost_to_reach or \
                       new_total_cost < min_cost_to_reach[(next_node_id, new_energy)]:
                        min_cost_to_reach[(next_node_id, new_energy)] = new_total_cost
                        heapq.heappush(pq, (new_total_cost, next_node_id, new_energy, new_path))
                else:
                  
                    pass # 

        if best_path_found:
            return {"path": best_path_found, "cost": min_total_cost}
        else:
            return {"path": [], "cost": -1} # No se encontró una ruta

    def create_order_from_route(self, source_node_id: str, destination_node_id: str, path_info: dict):
        # Lógica para crear una orden basada en la ruta encontrada
        self.order_counter += 1
        order_id = f"Order_{self.order_counter}"
        # Asume que ya tienes un cliente asociado o creas uno genérico
        client_id = "Client_001" # Esto debería ser dinámico

        new_order = {
            "ID": order_id,
            "cliente asociado": "Cliente Ejemplo",
            "cliente ID": client_id,
            "origen": source_node_id,
            "destino": destination_node_id,
            "status": "Completed",
            "fecha de creación": "2025-06-11", # Usar datetime.now()
            "prioridad": "Normal",
            "fecha entrega": "2025-06-11",
            "costo total": path_info["cost"]
        }
        self.orders[order_id] = new_order

        # Registrar la ruta en el AVL si se tiene esa funcionalidad
        # self.avl_routes.insert(path_info["path_tuple"], 1) # Asegúrate que tu AVL acepte tuplas como keys

        return order_id