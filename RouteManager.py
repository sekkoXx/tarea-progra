import math
import heapq
from collections import deque

class RouteManager:
    def __init__(self, graph):
        self.graph = graph

    def find_route_with_recharge(self,
                                 origin_id: int,
                                 dest_id: int,
                                 battery_limit: int = 50,
                                 method: str = "dijkstra"):
        """
        Encuentra la ruta desde origin_id hasta dest_id considerando recargas.
        method: "dijkstra" o "floyd-warshall"
        """
        if method == "dijkstra":
            return self._dijkstra_with_recharge(origin_id, dest_id, battery_limit)
        elif method == "floyd-warshall":
            return self._floyd_warshall_with_recharge(origin_id, dest_id, battery_limit)
        else:
            raise ValueError(f"Método desconocido: {method!r}")

    def _dijkstra_with_recharge(self, origin_id, dest_id, battery_limit):
        origin = self.graph.get_vertex(origin_id)
        dest   = self.graph.get_vertex(dest_id)
        Q = deque()
        Q.append((origin, battery_limit, [origin], [], 0))
        visited = {}  # (v, battery) -> cost
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

            # Recarga si corresponde
            if getattr(v, 'is_recharge', False) and v not in recharges:
                batt = battery_limit
                recharges = recharges + [v]

            for e in self.graph.incident_edges(v):
                w = e.opposite(v)
                c = e.cost()
                if batt >= c:
                    Q.append((w, batt - c, path + [w], recharges[:], cost + c))
        return None

    def _floyd_warshall_with_recharge(self, origin_id, dest_id, battery_limit):
        # 1) Preparación de vértices y mapeo a índices
        verts = list(self.graph.vertices())
        n = len(verts)
        ids = [v.element()['id'] for v in verts]
        id2idx = {vid: i for i, vid in enumerate(ids)}

        # 2) Inicializar matrices dist y nxt
        dist = [[math.inf] * n for _ in range(n)]
        nxt = [[None] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
            nxt[i][i] = ids[i]

        for v in verts:
            i = id2idx[v.element()['id']]
            for e in self.graph.incident_edges(v):
                w = e.opposite(v)
                j = id2idx[w.element()['id']]
                c = e.cost()
                if c < dist[i][j]:
                    dist[i][j] = c
                    dist[j][i] = c
                    nxt[i][j] = ids[j]
                    nxt[j][i] = ids[i]

        # 3) Ejecución de Floyd–Warshall
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        nxt[i][j] = nxt[i][k]

        # 4) Reconstrucción de subcamino entre dos vértices
        def build_subpath(u_id, v_id):
            i, j = id2idx[u_id], id2idx[v_id]
            if nxt[i][j] is None:
                return None
            path = [u_id]
            while u_id != v_id:
                u_id = nxt[id2idx[u_id]][j]
                path.append(u_id)
            return path

        # 5) Crear meta-grafo con nodos: origen, estaciones, destino
        recharge_ids = [v.element()['id'] for v in verts if getattr(v, 'is_recharge', False)]
        meta_nodes = [origin_id] + recharge_ids + [dest_id]
        meta_adj = {u: {} for u in meta_nodes}
        for u in meta_nodes:
            for v in meta_nodes:
                if u != v:
                    d = dist[id2idx[u]][id2idx[v]]
                    if d <= battery_limit:
                        meta_adj[u][v] = d

        # 6) Dijkstra sobre meta-grafo para encontrar secuencia de paradas
        pq = [(0, origin_id, [origin_id])]
        best = {origin_id: 0}
        meta_path = None
        total_cost = None
        while pq:
            cost_u, u, path_u = heapq.heappop(pq)
            if u == dest_id:
                meta_path = path_u
                total_cost = cost_u
                break
            if cost_u > best.get(u, math.inf):
                continue
            for v, w in meta_adj[u].items():
                nc = cost_u + w
                if nc < best.get(v, math.inf):
                    best[v] = nc
                    heapq.heappush(pq, (nc, v, path_u + [v]))
        if meta_path is None:
            return None

        # 7) Ensamblar ruta completa y lista de recargas
        full_path = []
        for idx in range(len(meta_path) - 1):
            seg = build_subpath(meta_path[idx], meta_path[idx + 1])
            if seg is None:
                return None
            if idx == 0:
                full_path.extend(seg)
            else:
                full_path.extend(seg[1:])
        recharges = [nid for nid in meta_path if nid not in (origin_id, dest_id)]

        return {
            'path': full_path,
            'total_cost': total_cost,
            'recharge_stops': recharges
        }