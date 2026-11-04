# 範例：使用 Python list 實作堆疊的基本操作（已完成，供參考）
class DemoStack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

demo = DemoStack()
demo.push("A")
demo.push("B")
print(demo.peek())      # 預期輸出：B
print(demo.pop())       # 預期輸出：B
print(demo.pop())       # 預期輸出：A
print(demo.is_empty())  # 預期輸出：True
