class Client:
    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name
        self.orders = []

    def add_order(self, order):
        """Agrega una orden a la lista de órdenes del cliente."""
        self.orders.append(order)

    def get_order_count(self):
        """Retorna la cantidad de órdenes asociadas a este cliente."""
        return len(self.orders)

    def to_dict(self):
        """Convierte el cliente a diccionario para mostrar en JSON."""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "total_orders": self.get_order_count()
        }
