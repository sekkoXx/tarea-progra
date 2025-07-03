class Client:
    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)


