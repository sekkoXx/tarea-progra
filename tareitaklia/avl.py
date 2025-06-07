class Node:
    def __init__(self, key, value):
        self.key = key              # Clave del nodo (puede ser string o cualquier tipo comparable)
        self.value = value          # Valor asociado a la clave
        self.left = None            # Hijo izquierdo
        self.right = None           # Hijo derecho
        self.height = 1             # Altura del nodo, inicialmente 1

class AVL:
    def __init__(self):
        self.root = None            # Raíz del árbol AVL

    def insert(self, key, value):
        """Inserta un par clave-valor en el árbol AVL."""
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        """Método recursivo privado para insertar un par clave-valor."""
        # Si el nodo es None, crear un nuevo nodo
        if not node:
            return Node(key, value)
        
        # Insertar en el subárbol izquierdo o derecho según la clave
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)

        # Actualizar la altura del nodo actual
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # Calcular el factor de balanceo
        balance = self._get_balance(node)

        # Realizar rotaciones si el árbol está desbalanceado
        if balance > 1:
            if key < node.left.key:  # Caso izquierda-izquierda
                return self._rotate_right(node)
            else:                    # Caso izquierda-derecha
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)
        if balance < -1:
            if key > node.right.key:  # Caso derecha-derecha
                return self._rotate_left(node)
            else:                     # Caso derecha-izquierda
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)

        return node

    def search(self, key):
        """Busca un nodo con la clave dada en el árbol AVL."""
        return self._search(self.root, key)

    def _search(self, node, key):
        """Método recursivo privado para buscar una clave."""
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def _get_height(self, node):
        """Obtiene la altura de un nodo (0 si es None)."""
        return node.height if node else 0

    def _get_balance(self, node):
        """Calcula el factor de balanceo de un nodo."""
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_left(self, z):
        """Realiza una rotación izquierda en el nodo z."""
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _rotate_right(self, z):
        """Realiza una rotación derecha en el nodo z."""
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

# Ejemplo de uso
if __name__ == "__main__":
    avl = AVL()
    # Insertar algunas rutas como prueba
    avl.insert("A → B → C", 1)
    avl.insert("A → D → E", 1)
    node = avl.search("A → B → C")
    if node:
        node.value += 1  # Incrementar la frecuencia
    print(f"Frecuencia de 'A → B → C': {avl.search('A → B → C').value}")  # Debería mostrar 2
    print(f"Frecuencia de 'A → D → E': {avl.search('A → D → E').value}")  # Debería mostrar 1