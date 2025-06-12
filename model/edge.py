class Edge:
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