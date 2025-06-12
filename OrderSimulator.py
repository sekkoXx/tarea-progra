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
        order_id = f"O{self.tracker.get_next_order_id()}"
        path = route['path']
        cost = route['total_cost']
        recs = route.get('recharge_stops', [])
        self.tracker.register_route(path, cost)
        print(f"Ruta de {origin_id} a {dest_id}:")
        print(f"Ruta: {'→'.join(map(str,path))}")
        print(f"Costo: {cost} | Paradas de recarga: {recs} | Estado: Entregado\n")
        return path, cost, recs, origin_id, dest_id, order_id

    def process_orders(self, n=5):
        resultados = []
        for i in range(1, n+1):
            o = random.choice(self.warehouses)
            d = random.choice(self.clients)
            resultado = self.process_origen_destino(o.element()['id'], d.element()['id'])
            if resultado:
                resultados.append({
                    'order_id': resultado[5],
                    'origin': resultado[3],
                    'dest': resultado[4],
                    'path': resultado[0],
                    'cost': resultado[1],
                    'recharges': resultado[2]
                })
        return resultados