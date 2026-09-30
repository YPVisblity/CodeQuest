def inorder(node, result=None):
    """中序走訪：左子樹 -> 根 -> 右子樹"""
    if result is None:
        result = []
    # TODO: 請完成這個函式
    return result


def postorder(node, result=None):
    """後序走訪：左子樹 -> 右子樹 -> 根"""
    if result is None:
        result = []
    # TODO: 請完成這個函式
    return result

# ===== 自我檢查 =====
assert inorder(root) == ['D', 'B', 'E', 'A', 'C']
assert postorder(root) == ['D', 'E', 'B', 'C', 'A']

r1 = inorder(root)
r2 = inorder(root)
assert r1 == r2 == ['D', 'B', 'E', 'A', 'C'], "檢查是否誤用可變預設參數"

print("恭喜！基礎任務全部通過，可以繼續挑戰進階任務。")

