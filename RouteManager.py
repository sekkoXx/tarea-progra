from collections import deque

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