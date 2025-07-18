#!/usr/bin/env python3
import random
from collections import deque

# ------------------- Clases Base -------------------

from model.graph import Graph
from model.vertex import Vertex
from model.edge import Edge

# ------------------- AVL Tree -------------------

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1

class AVL:
    def __init__(self):
        self.root = None
    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)
    def _insert(self, node, key, value):
        if node is None:
            return Node(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value += value
            return node
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        balance = self._balance(node)
        if balance > 1:
            if key < node.left.key:
                return self._rotate_right(node)
            else:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        if balance < -1:
            if key > node.right.key:
                return self._rotate_left(node)
            else:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)
        return node
    def _height(self, node):
        return node.height if node else 0
    def _balance(self, node):
        return self._height(node.left) - self._height(node.right)
    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y
    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

# ------------------- RouteManager Mejorado -------------------

class RouteManager:
    def __init__(self, graph):
        self.graph = graph

    def find_route_with_recharge(self, origin_id, dest_id, battery_limit=50):
        origin = self.graph.get_vertex(origin_id)
        dest = self.graph.get_vertex(dest_id)
        Q = deque()
        Q.append((origin, battery_limit, [origin], [], 0))
        visited = dict()  # (v, battery): cost acumulado
        while Q:
            v, batt, path, recharges, cost = Q.popleft()
            if v == dest:
                return {
                    'path': [x.element()['id'] for x in path],
                    'total_cost': cost,
                    'recharge_stops': [x.element()['id'] for x in recharges]
                }
            state = (v, batt)
            if state in visited and visited[state] <= cost:
                continue
            visited[state] = cost
            if v.is_recharge and v not in recharges:
                batt = battery_limit
                recharges = recharges + [v]
            for e in self.graph.incident_edges(v):
                w = e.opposite(v)
                c = e.cost()
                if batt >= c:
                    Q.append((w, batt - c, path + [w], recharges[:], cost + c))
        return None

# ------------------- RouteTracker -------------------

class RouteTracker:
    def __init__(self):
        self.avl = AVL()
        self.node_map = {}
    def register_route(self, path_ids, cost):
        key = '→'.join(map(str, path_ids))
        self.avl.insert(key, 1)
        for vid in path_ids:
            self.node_map[vid] = self.node_map.get(vid, 0) + 1
    def get_most_frequent_routes(self, n=5):
        results = []
        def inorder(node):
            if not node: return
            inorder(node.left)
            results.append((node.key, node.value))
            inorder(node.right)
        inorder(self.avl.root)
        return sorted(results, key=lambda x: x[1], reverse=True)[:n]
    def get_node_visit_stats(self):
        return dict(sorted(self.node_map.items(), key=lambda x: x[1], reverse=True))

# ------------------- RouteOptimizer -------------------

class RouteOptimizer:
    def __init__(self, tracker, manager):
        self.tracker = tracker
        self.manager = manager
    def suggest_optimized_route(self, origin_id, dest_id):
        history = self.tracker.get_most_frequent_routes(10)
        best = None
        best_score = float('inf')
        for route_str, freq in history:
            ids = list(map(int, route_str.split('→')))
            if ids[0] == origin_id and ids[-1] == dest_id:
                cost_est = len(ids) - 1
                score = cost_est / (freq or 1)
                if score < best_score:
                    best_score, best = score, ids
        if best:
            return {
                'path': best,
                'total_cost': (len(best) - 1)*10,
                'recharge_stops': []
            }
        return self.manager.find_route_with_recharge(origin_id, dest_id)
    def get_optimization_report(self):
        hist = self.tracker.get_most_frequent_routes()
        report = "Decisiones de optimización:\n"
        report += "Se priorizaron rutas frecuentes y bajo costo.\nTop segmentos:\n"
        segs = {}
        for route, freq in hist:
            pts = route.split('→')
            for i in range(len(pts)-1):
                seg = f"{pts[i]}→{pts[i+1]}"
                segs[seg] = segs.get(seg, 0) + freq
        top = sorted(segs.items(), key=lambda x: x[1], reverse=True)[:5]
        for seg, cnt in top:
            report += f"{seg}: {cnt} usos\n"
        return report

# ------------------- OrderSimulator -------------------

class OrderSimulator:
    def __init__(self, graph, manager, tracker, optimizer):
        self.graph = graph
        self.manager = manager
        self.tracker = tracker
        self.optimizer = optimizer
        self.warehouses = [v for v in graph.vertices() if v.is_warehouse]
        self.clients = [v for v in graph.vertices() if v.is_client]
    def process_orders(self, n=5):
        for i in range(1, n+1):
            o = random.choice(self.warehouses)
            d = random.choice(self.clients)
            route = self.optimizer.suggest_optimized_route(o.element()['id'], d.element()['id'])
            if not route:
                print(f"Orden #{i}: No se encontró ruta de {o.element()['id']} a {d.element()['id']}")
                continue
            path = route['path']
            cost = route['total_cost']
            recs = route.get('recharge_stops', [])
            self.tracker.register_route(path, cost)
            print(f"Orden #{i}: {o.element()['id']} → {d.element()['id']}")
            print(f"Ruta: {'→'.join(map(str,path))}")
            print(f"Costo: {cost} | Paradas de recarga: {recs} | Estado: Entregado\n")

# ------------------- MAIN -------------------

if __name__ == "__main__":
    g = Graph()
    verts = []
    for i in range(15):
        verts.append(g.insert_vertex({
            'id': i,
            'almacen': (i == 0 or i == 1),
            'cliente': (i >= 12),
            'estacion': (i % 4 == 0 and i != 0)
        }))
    for i in range(len(verts) - 1):
        g.insert_edge(verts[i], verts[i+1], cost=12)

    rm = RouteManager(g)
    rt = RouteTracker()
    ro = RouteOptimizer(rt, rm)
    sim = OrderSimulator(g, rm, rt, ro)

    sim.process_orders(5)
    print("Rutas más frecuentes:", rt.get_most_frequent_routes())
    print("Estadísticas de visitas por nodo:", rt.get_node_visit_stats())
    print(ro.get_optimization_report())
