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