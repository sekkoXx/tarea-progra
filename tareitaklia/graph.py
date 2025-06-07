class Graph:
    def __init__(self, directed=False):
        """Inicializa el grafo como dirigido o no dirigido."""
        self._outgoing = {}        # Diccionario: vértice -> adyacentes
        self._incoming = {} if directed else self._outgoing
        self._directed = directed  # Tipo de grafo: True si es dirigido

    def is_directed(self):
        """Indica si el grafo es dirigido."""
        return self._directed

    def insert_vertex(self, element):
        """Crea un nuevo vértice y lo agrega al grafo."""
        v = Vertex(element)
        self._outgoing[v] = {}    # Agrega vértice al diccionario de salidas
        if self._directed:
            self._incoming[v] = {}  # Solo si es dirigido, agrega entrada
        return v

    def insert_edge(self, u, v, element):
        """Crea y agrega una arista entre dos vértices dados."""
        e = Edge(u, v, element)
        self._outgoing[u][v] = e   # Agrega arista a salidas
        self._incoming[v][u] = e   # Agrega arista a entradas
        return e

    def remove_edge(self, u, v):
        """Elimina la arista entre u y v, si existe."""
        if u in self._outgoing and v in self._outgoing[u]:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    def remove_vertex(self, v):
        """Elimina un vértice y todas sus aristas incidentes."""
        for u in list(self._outgoing.get(v, {})):
            self.remove_edge(v, u)
        for u in list(self._incoming.get(v, {})):
            self.remove_edge(u, v)
        self._outgoing.pop(v, None)
        if self._directed:
            self._incoming.pop(v, None)

    def get_edge(self, u, v):
        """Retorna la arista desde u hasta v, o None si no existe."""
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        """Retorna todos los vértices del grafo."""
        return self._outgoing.keys()

    def edges(self):
        """Retorna todas las aristas del grafo."""
        seen = set()
        for adj_map in self._outgoing.values():
            seen.update(adj_map.values())
        return seen

    def neighbors(self, v):
        """Retorna los vecinos del vértice v."""
        return self._outgoing[v].keys()

    def degree(self, v, outgoing=True):
        """Retorna el grado de un vértice (saliente o entrante)."""
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        """Retorna las aristas incidentes al vértice v."""
        adj = self._outgoing if outgoing else self._incoming
        return adj[v].values()

    def dfs(self, start, visited=None):
        """Recorrido en profundidad (DFS) desde el vértice dado."""
        if visited is None:
            visited = set()
        visited.add(start)
        yield start
        for neighbor in self.neighbors(start):
            if neighbor not in visited:
                yield from self.dfs(neighbor, visited)

    def bfs(self, start):
        """Recorrido en anchura (BFS) desde el vértice dado."""
        visited = set()
        queue = [start]
        visited.add(start)
        while queue:
            v = queue.pop(0)
            yield v
            for neighbor in self.neighbors(v):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    def topological_sort(self):
        """Ordenamiento topológico de un grafo dirigido acíclico."""
        in_degree = {v: 0 for v in self.vertices()}
        for u in self.vertices():
            for v in self.neighbors(u):
                in_degree[v] += 1

        queue = [v for v in self.vertices() if in_degree[v] == 0]
        result = []

        while queue:
            u = queue.pop(0)
            result.append(u)
            for v in self.neighbors(u):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(result) != len(in_degree):
            raise ValueError("Graph has a cycle. Topological sort not possible.")
        return result

    def get_vertex(self, element):
        """Busca y devuelve el vértice con el elemento dado."""
        for v in self.vertices():
            if v.element() == element:
                return v
        return None