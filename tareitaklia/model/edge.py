class Edge:
    """Clase que representa una arista (conexión) entre dos vértices."""
    __slots__ = '_origin', '_destination', '_element'

    def __init__(self, u, v, x):
        """Inicializa la arista con dos vértices y un valor asociado."""
        self._origin = u      # Vértice de origen
        self._destination = v # Vértice de destino
        self._element = x     # Elemento asociado a la arista (e.g., costo)

    def endpoints(self):
        """Devuelve una tupla con los dos extremos de la arista (u, v)."""
        return (self._origin, self._destination)  # Devolver _origin y _destination

    def opposite(self, v):
        """Devuelve el vértice opuesto a v en esta arista."""
        return self._destination if v is self._origin else self._origin  # Retornar el opuesto

    def element(self):
        """Devuelve el valor asociado a esta arista."""
        return self._element  # Retornar _element

    def __hash__(self):
        """Permite usar la arista como clave en estructuras tipo set/map."""
        return hash((self._origin, self._destination))  # Usar _origin y _destination

    def __str__(self):
        """Representación en string de la arista."""
        return f"({self._origin}->{self._destination}):{self._element}"  # Usar origin, destination y element

    def __repr__(self):
        """Representación oficial de la arista."""
        return f"Edge({self._origin}, {self._destination}, {self._element})"  # Usar los atributos