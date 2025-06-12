from avl_tree import AVL, Node

class RouteTracker:
    def __init__(self):
        self.avl = AVL()
        self.node_map = {}
    def register_route(self, path_ids, cost):
        key = '→'.join(map(str, path_ids))
        self.avl.insert(key, 1)
        for vid in path_ids:
            self.node_map[vid] = self.node_map.get(vid, 0) + 1
    def get_most_frequent_routes(self, n=5):
        results = []
        def inorder(node):
            if not node: return
            inorder(node.left)
            results.append((node.key, node.value))
            inorder(node.right)
        inorder(self.avl.root)
        return sorted(results, key=lambda x: x[1], reverse=True)[:n]
    def get_node_visit_stats(self):
        return dict(sorted(self.node_map.items(), key=lambda x: x[1], reverse=True))