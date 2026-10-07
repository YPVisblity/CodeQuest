# 範例：Node 類別定義（已完成，供參考）
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

# 範例：走訪並印出串列內容
def print_list(head):
    current = head
    result = []
    while current is not None:
        result.append(str(current.data))
        current = current.next
    print(" -> ".join(result) if result else "(空串列)")

# 快速手動建立一個串列 1 -> 2 -> 3 來測試 print_list
n1 = Node(1)
n2 = Node(2)
n3 = Node(3)
n1.next = n2
n2.next = n3
print_list(n1)   # 預期輸出：1 -> 2 -> 3
