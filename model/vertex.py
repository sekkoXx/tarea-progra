class Vertex:
    __slots__ = ('_element', 'is_warehouse', 'is_client', 'is_recharge')
    def __init__(self, element):
        self._element = element
        self.is_warehouse = element.get('almacen', False)
        self.is_client = element.get('cliente', False)
        self.is_recharge = element.get('estacion', False)
    def element(self):
        return self._element
    def __hash__(self):
        return hash(id(self))
    def __str__(self):
        return str(self._element['id'])
    def __repr__(self):
        """Representación oficial de la clase Vertex."""
        return f"Vertex({self._element})"  # Usar _element