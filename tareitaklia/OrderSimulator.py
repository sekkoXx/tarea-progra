import random

class OrderSimulator:
    def __init__(self, graph, route_manager, route_tracker, route_optimizer):
        """Inicializa el simulador con las dependencias necesarias."""
        self.graph = graph
        self.route_manager = route_manager
        self.route_tracker = route_tracker
        self.route_optimizer = route_optimizer
        self.warehouses = [v for v in graph.vertices() if v.is_warehouse]
        self.clients = [v for v in graph.vertices() if v.is_client]

    def process_orders(self, num_orders=10):
        """Procesa un número dado de órdenes."""
        for i in range(num_orders):
            origin = random.choice(self.warehouses)
            destination = random.choice(self.clients)
            route = self.route_optimizer.suggest_optimized_route(origin.element(), destination.element())
            if route:
                self.route_tracker.register_route(route['path'], route['total_cost'])
                print(f"Orden #{i+1}: {origin.element()} → {destination.element()}")
                print(f"Ruta: {' → '.join(route['path'])}")
                print(f"Costo: {route['total_cost']} | Paradas de recarga: {route['recharge_stops']} | Estado: Entregado")
            else:
                print(f"Orden #{i+1}: No se pudo encontrar ruta de {origin.element()} a {destination.element()}")