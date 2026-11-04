def find_min(node):
    """回傳以 node 為根的子樹中，資料值最小的節點"""
    current = node
    while current.left is not None:
        current = current.left
    return current


def delete_node(root, data):
    """刪除 BST 中資料值等於 data 的節點，回傳刪除後的樹根"""
    if root is None:
        return root
    # TODO: 請完成這個函式（需處理三種情況：葉節點、單一子節點、兩個子節點）
    return root