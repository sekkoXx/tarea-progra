class RouteManager:
    def __init__(self, graph):
        """Inicializa el gestor de rutas con un grafo."""
        self.graph = graph

    def find_nearest_recharge(self, vertex):
        """Encuentra la estación de recarga más cercana entre los vecinos."""
        for neighbor in self.graph.neighbors(vertex):
            if neighbor.is_recharge:
                return neighbor
        return None

    def find_route_with_recharge(self, origin_id, destination_id, battery_limit=50):
        """Encuentra la ruta óptima desde origin_id hasta destination_id con recargas."""
        origin = self.graph.get_vertex(origin_id)
        destination = self.graph.get_vertex(destination_id)
        if not origin or not destination:
            return None

        queue = [(origin, [origin], 0, [], [[]], 0)]  # (current, path, total_cost, recharge_stops, segments, segment_cost)
        visited = set()

        while queue:
            current, path, total_cost, recharge_stops, segments, segment_cost = queue.pop(0)
            if current == destination:
                segments[-1] = path[len(segments[-2]) if segments[-2] else 0:]
                return {
                    'path': [v.element() for v in path],
                    'total_cost': total_cost,
                    'recharge_stops': [v.element() for v in recharge_stops],
                    'segments': [[v.element() for v in seg] for seg in segments]
                }

            if current in visited:
                continue
            visited.add(current)

            for edge in self.graph.incident_edges(current):
                next_vertex = edge.opposite(current)
                edge_cost = edge.element()
                new_total_cost = total_cost + edge_cost
                new_segment_cost = segment_cost + edge_cost

                if new_segment_cost > battery_limit:
                    recharge_station = self.find_nearest_recharge(current)
                    if recharge_station and recharge_station not in visited:
                        recharge_edge = self.graph.get_edge(current, recharge_station)
                        if recharge_edge:
                            new_path = path + [recharge_station]
                            new_recharge_stops = recharge_stops + [recharge_station]
                            new_segments = segments[:-1] + [path[len(segments[-2]) if segments[-2] else 0:] + [recharge_station]], [recharge_station]
                            queue.append((recharge_station, new_path, total_cost + recharge_edge.element(),
                                          new_recharge_stops, new_segments, 0))
                else:
                    new_path = path + [next_vertex]
                    new_segments = segments.copy()
                    new_segments[-1] = path[len(segments[-2]) if segments[-2] else 0:] + [next_vertex]
                    queue.append((next_vertex, new_path, new_total_cost, recharge_stops, new_segments, new_segment_cost))

        return None