class RouteTracker:
    def __init__(self):
        self.route_frequency = AVL()  # Usar AVL proporcionado
        self.node_visits = self.create_custom_hashmap()

    def create_custom_hashmap(self, initial_size=10):
        """Implementa un HashMap básico usando listas"""
        return [[] for _ in range(initial_size)]

    def _hash(self, key, size):
        return hash(key) % size

    def _update_node_visits(self, node_id):
        """Actualiza el conteo de visitas en el HashMap"""
        size = len(self.node_visits)
        index = self._hash(node_id, size)
        bucket = self.node_visits[index]
        for i, (k, v) in enumerate(bucket):
            if k == node_id:
                bucket[i] = (k, v + 1)
                return
        bucket.append((node_id, 1))

    def register_route(self, route_path, cost):
        """Registra una ruta en las estadísticas"""
        route_str = " → ".join(route_path)
        node = self.route_frequency.search(route_str)
        if node:
            node.value += 1  # Incrementar directamente el valor del nodo
        else:
            self.route_frequency.insert(route_str, 1)
        for node in route_path:
            self._update_node_visits(node)

    def get_most_frequent_routes(self, top_n=5):
        """Retorna las N rutas más utilizadas"""
        routes = []
        def inorder(node):
            if node:
                inorder(node.left)
                routes.append((node.key, node.value))
                inorder(node.right)
        inorder(self.route_frequency.root)
        return sorted(routes, key=lambda x: x[1], reverse=True)[:top_n]

    def get_node_visit_stats(self):
        """Estadísticas de visitas por nodo"""
        stats = {}
        for bucket in self.node_visits:
            for node_id, count in bucket:
                stats[node_id] = count
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))