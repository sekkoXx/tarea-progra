class RouteOptimizer:
    def __init__(self, route_tracker, route_manager):
        """Inicializa el optimizador con un rastreador y gestor de rutas."""
        self.route_tracker = route_tracker
        self.route_manager = route_manager

    def suggest_optimized_route(self, origin_id, destination_id):
        """Sugiere una ruta optimizada basada en historial o cálculo."""
        frequent_routes = self.route_tracker.get_most_frequent_routes(top_n=10)
        for route_str, _ in frequent_routes:
            nodes = route_str.split(" → ")
            if nodes[0] == origin_id and nodes[-1] == destination_id:
                path = [self.route_manager.graph.get_vertex(node) for node in nodes]
                total_cost = sum(self.route_manager.graph.get_edge(path[i], path[i+1]).element()
                                 for i in range(len(path)-1))
                return {
                    'path': nodes,
                    'total_cost': total_cost,
                    'recharge_stops': [],
                    'segments': [nodes]
                }
        return self.route_manager.find_route_with_recharge(origin_id, destination_id)

    def analyze_route_patterns(self):
        """Analiza patrones en las rutas frecuentes."""
        frequent_routes = self.route_tracker.get_most_frequent_routes()
        patterns = {}
        for route_str, freq in frequent_routes:
            nodes = route_str.split(" → ")
            for i in range(len(nodes) - 1):
                segment = f"{nodes[i]} → {nodes[i+1]}"
                patterns[segment] = patterns.get(segment, 0) + freq
        return sorted(patterns.items(), key=lambda x: x[1], reverse=True)

    def get_optimization_report(self):
        """Genera un reporte de optimización."""
        patterns = self.analyze_route_patterns()
        report = "Reporte de Optimización:\n"
        report += "Segmentos más frecuentes:\n"
        for segment, count in patterns[:5]:
            report += f"{segment}: {count} veces\n"
        return report