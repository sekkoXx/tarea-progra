#!/usr/bin/env python3
import random

# --- Clases Base: Vertex, Edge, Graph, AVL ---

class Vertex:
    __slots__ = ('_element', 'is_warehouse', 'is_client', 'is_recharge')

    def __init__(self, element):
        # element es un dict con llaves: 'id', 'almacen', 'cliente', 'estacion'
        self._element = element
        self.is_warehouse = element.get('almacen', False)
        self.is_client = element.get('cliente', False)
        self.is_recharge = element.get('estacion', False)

    def element(self):
        return self._element

    def __hash__(self):
        return hash(id(self))

    def __str__(self):
        return str(self._element['id'])

class Edge:
    __slots__ = ('_origin', '_destination', '_cost')

    def __init__(self, u, v, cost):
        self._origin = u
        self._destination = v
        self._cost = cost

    def endpoints(self):
        return (self._origin, self._destination)

    def opposite(self, v):
        return self._destination if v is self._origin else self._origin

    def cost(self):
        return self._cost

    def __hash__(self):
        return hash((self._origin, self._destination))

class Graph:
    def __init__(self, directed=False):
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
        self._directed = directed

    def insert_vertex(self, element):
        v = Vertex(element)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def insert_edge(self, u, v, cost):
        e = Edge(u, v, cost)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e

    def get_edge(self, u, v):
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        return self._outgoing.keys()

    def neighbors(self, v):
        return self._outgoing[v].keys()

    def incident_edges(self, v):
        return self._outgoing[v].values()

    def get_vertex(self, id_):
        for v in self.vertices():
            if v.element().get('id') == id_:
                return v
        return None

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

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

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

# --- Parte 1: Algoritmo de Ruta con Recarga Inteligente ---

class RouteManager:
    def __init__(self, graph):
        self.graph = graph

    def find_nearest_recharge(self, vertex):
        for nbr in self.graph.neighbors(vertex):
            if nbr.is_recharge:
                return nbr
        return None

    def find_route_with_recharge(self, origin_id, dest_id, battery_limit=50):
        origin = self.graph.get_vertex(origin_id)
        dest = self.graph.get_vertex(dest_id)
        # BFS con estado (vértice, batería actual, ruta, recargas, costo acumulado)
        from collections import deque
        Q = deque()
        Q.append((origin, battery_limit, [origin], [], 0))
        visited = set()
        while Q:
            v, batt, path, recharges, cost = Q.popleft()
            if v == dest:
                return {
                    'path': [x.element()['id'] for x in path],
                    'total_cost': cost,
                    'recharge_stops': [x.element()['id'] for x in recharges]
                }
            state = (v, batt)
            if state in visited:
                continue
            visited.add(state)
            for e in self.graph.incident_edges(v):
                w = e.opposite(v)
                c = e.cost()
                if c <= batt:
                    Q.append((w, batt - c, path + [w], recharges[:], cost + c))
                else:
                    station = self.find_nearest_recharge(v)
                    if station and station not in recharges:
                        # ir a estación, recargar, luego mismo vecino
                        e2 = self.graph.get_edge(v, station)
                        if e2:
                            Q.append((w,
                                      battery_limit - c,
                                      path + [station, w],
                                      recharges + [station],
                                      cost + e2.cost() + c))
        return None

# --- Parte 2: Sistema de Registro de Rutas ---

class RouteTracker:
    def __init__(self):
        self.avl = AVL()
        self.node_map = {}  # conteo de visitas por nodo

    def register_route(self, path_ids, cost):
        # ruta como string "A→B→C"
        key = '→'.join(map(str, path_ids))
        self.avl.insert(key, 1)
        for vid in path_ids:
            self.node_map[vid] = self.node_map.get(vid, 0) + 1

    def get_most_frequent_routes(self, n=5):
        # recorrido inorder + sort
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

# --- Parte 3: Optimizador de Rutas Recurrentes ---

class RouteOptimizer:
    def __init__(self, tracker, manager):
        self.tracker = tracker
        self.manager = manager

    def suggest_optimized_route(self, origin_id, dest_id):
        history = self.tracker.get_most_frequent_routes(10)
        # heurística: combinar freq y costo
        best = None
        best_score = float('inf')
        for route_str, freq in history:
            ids = list(map(int, route_str.split('→')))
            if ids[0] == origin_id and ids[-1] == dest_id:
                cost_est = len(ids) - 1  # estimado
                score = cost_est / (freq or 1)
                if score < best_score:
                    best_score, best = score, ids
        if best:
            return {
                'path': best,
                'total_cost': (len(best) - 1)*10,  # sup costo medio
                'recharge_stops': []
            }
        # si no hay historial, uso manager
        return self.manager.find_route_with_recharge(origin_id, dest_id)

    def get_optimization_report(self):
        hist = self.tracker.get_most_frequent_routes()
        report = "Decisiones de optimización:\n"
        report += "Se priorizaron rutas frecuentes y bajo costo.\n"
        report += "Top segmentos:\n"
        # contar segmentos
        segs = {}
        for route, freq in hist:
            pts = route.split('→')
            for i in range(len(pts)-1):
                seg = f"{pts[i]}→{pts[i+1]}"
                segs[seg] = segs.get(seg,0) + freq
        top = sorted(segs.items(), key=lambda x: x[1], reverse=True)[:5]
        for seg, cnt in top:
            report += f"{seg}: {cnt} usos\n"
        return report

# --- Parte 4: Simulador de Órdenes ---

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

# --- Main para demostración ---

if __name__ == "__main__":
    # crear grafo de ejemplo
    g = Graph()
    verts = []
    for i in range(10):
        verts.append(g.insert_vertex({
            'id': i,
            'almacen': (i==0 or i==1),
            'cliente': (i>=8),
            'estacion': (i%3==0 and i not in (0,))
        }))
    # unir linealmente
    for i in range(9):
        g.insert_edge(verts[i], verts[i+1], cost=10)

    rm = RouteManager(g)
    rt = RouteTracker()
    ro = RouteOptimizer(rt, rm)
    sim = OrderSimulator(g, rm, rt, ro)

    # Procesar y mostrar
    sim.process_orders(5)
    print("Rutas más frecuentes:", rt.get_most_frequent_routes())
    print("Estadísticas de visitas por nodo:", rt.get_node_visit_stats())
    print(ro.get_optimization_report())
