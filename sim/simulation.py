from collections import deque
from model.graph import Graph
from model.vertex import Vertex

from RouteManager import RouteManager
from RouteTracker import RouteTracker
from RouteOptimizer import RouteOptimizer
from OrderSimulator import OrderSimulator

class Simulation:
    def __init__(self, graph=None):
        self.graph = graph
        self.orders = {}
        self.order_count = 1
        self.clients = []
        if graph is not None:
            self.clients = [v for v in graph.vertices() if v.is_client]
        self.routes = {}
        self.route_manager = RouteManager(graph)
        self.route_tracker = RouteTracker()
        self.route_optimizer = RouteOptimizer(self.route_tracker, self.route_manager)
        self.order_simulator = OrderSimulator(self.graph, self.route_manager, self.route_tracker, self.route_optimizer)
        
    def create_order_from_route(self, origin_id: int, dest_id: int, path_info: dict) -> str:
        """
        Crea una orden usando la información de ruta calculada
        y la almacena en el diccionario self.orders.
        Devuelve el ID de la orden.
        """
        oid = f"O{self.order_count}"
        self.orders[oid] = {
            "origin": origin_id,
            "dest": dest_id,
            "path": path_info.get("path", []),
            "cost": path_info.get("total_cost", 0),
            "recharges": path_info.get("recharge_stops", [])
        }
        self.order_count += 1
        # Registrar ruta en el tracker si es posible
        if hasattr(self.route_tracker, 'record_route'):
            self.route_tracker.record_route(self.orders[oid]["path"])
        return oid

    '''def find_route_with_recharge(self, origin_id, dest_id, max_autonomy=50):
        origin = self.graph.get_vertex(origin_id)
        dest = self.graph.get_vertex(dest_id)
        Q = deque()
        Q.append((origin, max_autonomy, [origin], [], 0))
        visited = dict()

        while Q:
            v, batt, path, recharges, cost = Q.popleft()
            if v == dest:
                return {
                    "path": [x.element()['id'] for x in path],
                    "cost": cost,
                    "recharge_stops": [x.element()['id'] for x in recharges]
                }
            state = (v, batt)
            if state in visited and visited[state] <= cost:
                continue
            visited[state] = cost
            if v.is_recharge and v not in recharges:
                batt = max_autonomy
                recharges = recharges + [v]
            for e in self.graph.incident_edges(v):
                w = e.opposite(v)
                c = e.element()
                if batt >= c:
                    Q.append((w, batt - c, path + [w], recharges[:], cost + c))
        return None

    def create_order_from_route(self, origin_id, dest_id, path_info):
        oid = f"O{self.order_count}"
        self.orders[oid] = {
            "origin": origin_id,
            "dest": dest_id,
            "path": path_info["path"],
            "cost": path_info["cost"],
            "recharges": path_info.get("recharge_stops", [])
        }
        self.order_count += 1
        return oid
'''