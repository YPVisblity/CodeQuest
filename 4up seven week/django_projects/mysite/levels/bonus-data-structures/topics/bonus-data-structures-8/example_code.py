class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

# 手動建立一棵範例樹：
#         A
#        / \
#       B   C
#      / \
#     D   E
root = TreeNode("A")
root.left = TreeNode("B")
root.right = TreeNode("C")
root.left.left = TreeNode("D")
root.left.right = TreeNode("E")

# 範例：前序走訪（已完成，供參考）
def preorder(node, result=None):
    if result is None:
        result = []
    if node is not None:
        result.append(node.data)
        preorder(node.left, result)
        preorder(node.right, result)
    return result

print(preorder(root))   # 預期輸出：['A', 'B', 'D', 'E', 'C']
