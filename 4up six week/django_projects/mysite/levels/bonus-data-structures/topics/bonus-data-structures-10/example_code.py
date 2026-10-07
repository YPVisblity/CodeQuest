class BSTNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

# 範例：插入操作（已完成，供參考）
def insert(root, data):
    if root is None:
        return BSTNode(data)
    if data < root.data:
        root.left = insert(root.left, data)
    elif data > root.data:
        root.right = insert(root.right, data)
    return root

def inorder_values(node, result=None):
    if result is None:
        result = []
    if node is not None:
        inorder_values(node.left, result)
        result.append(node.data)
        inorder_values(node.right, result)
    return result

# 手動建立一棵 BST 來測試
bst_root = None
for value in [8, 3, 10, 1, 6, 14]:
    bst_root = insert(bst_root, value)

print(inorder_values(bst_root))  # 預期輸出：[1, 3, 6, 8, 10, 14]（中序走訪結果應為由小到大排序）
