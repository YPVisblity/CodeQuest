from collections import deque
# 範例：使用 deque 實作佇列的基本操作（已完成，供參考）
class DemoQueue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.popleft()

    def peek(self):
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

demo = DemoQueue()
demo.enqueue("客人A")
demo.enqueue("客人B")
print(demo.peek())      # 預期輸出：客人A
print(demo.dequeue())   # 預期輸出：客人A
print(demo.dequeue())   # 預期輸出：客人B