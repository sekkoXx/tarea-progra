from typing import List, Tuple

class UnionFind:
    def __init__(self, elements):
        # parent pointer and rank
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        return True

class RouteOptimizer:
    def __init__(self, tracker, manager):
        self.tracker = tracker
        self.manager = manager

    def kruskal_mst(self, graph) -> List[Tuple]:
        """
        Genera el árbol de expansión mínima (MST) del grafo usando Kruskal.
        Asume grafo no dirigido. Retorna lista de tuplas (u, v, weight).
        """
        # Recolectar todas las aristas sin duplicados
        edges = []
        seen = set()
        for u in graph.vertices():
            for e in graph.incident_edges(u):
                v = e.opposite(u)
                key = tuple(sorted((u.element()['id'], v.element()['id'])))
                if key in seen:
                    continue
                seen.add(key)
                edges.append((e.cost(), u, v))
        # Ordenar por peso ascendente
        edges.sort(key=lambda x: x[0])

        # Inicializar Union-Find con todos los vértices
        vertices = [v for v in graph.vertices()]
        uf = UnionFind(vertices)

        mst = []
        for weight, u, v in edges:
            if uf.union(u, v):
                mst.append((u, v, weight))
        return mst

    def suggest_optimized_route(self, origin_id: int, dest_id: int):
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
                'total_cost': (len(best) - 1) * 10,
                'recharge_stops': []
            }
        return self.manager.find_route_with_recharge(origin_id, dest_id)

    def get_optimization_report(self) -> str:
        hist = self.tracker.get_most_frequent_routes()
        report = "Decisiones de optimización:\n"
        report += "Se priorizaron rutas frecuentes y bajo costo.\nTop segmentos:\n"
        segs = {}
        for route, freq in hist:
            pts = route.split('→')
            for i in range(len(pts) - 1):
                seg = f"{pts[i]}→{pts[i+1]}"
                segs[seg] = segs.get(seg, 0) + freq
        top = sorted(segs.items(), key=lambda x: x[1], reverse=True)[:5]
        for seg, cnt in top:
            report += f"{seg}: {cnt} usos\n"
        return report
