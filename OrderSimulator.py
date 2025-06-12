import random

class OrderSimulator:
    def __init__(self, graph, manager, tracker, optimizer):
        self.graph = graph
        self.manager = manager
        self.tracker = tracker
        self.optimizer = optimizer
        self.warehouses = [v for v in graph.vertices() if v.is_warehouse]
        self.clients = [v for v in graph.vertices() if v.is_client]

    def process_origen_destino(self, origin_id, dest_id):
        print(f"Procesando orden de {origin_id} a {dest_id}...")
        route = self.optimizer.suggest_optimized_route(origin_id, dest_id)
        if not route:
            print(f"No se encontró ruta de {origin_id} a {dest_id}")
            return None
        path = route['path']
        cost = route['total_cost']
        recs = route.get('recharge_stops', [])
        self.tracker.register_route(path, cost)
        print(f"Ruta de {origin_id} a {dest_id}:")
        print(f"Ruta: {'→'.join(map(str,path))}")
        print(f"Costo: {cost} | Paradas de recarga: {recs} | Estado: Entregado\n")
        return path, cost, recs

    def process_orders(self, n=5):
        for i in range(1, n+1):
            o = random.choice(self.warehouses)
            d = random.choice(self.clients)
            self.process_origen_destino(o.element()['id'], d.element()['id'])

            # Codigo antiguo
            '''route = self.optimizer.suggest_optimized_route(o.element()['id'], d.element()['id'])
            if not route:
                print(f"Orden #{i}: No se encontró ruta de {o.element()['id']} a {d.element()['id']}")
                continue
            path = route['path']
            cost = route['total_cost']
            recs = route.get('recharge_stops', [])
            self.tracker.register_route(path, cost)
            print(f"Orden #{i}: {o.element()['id']} → {d.element()['id']}")
            print(f"Ruta: {'→'.join(map(str,path))}")
            print(f"Costo: {cost} | Paradas de recarga: {recs} | Estado: Entregado\n")'''