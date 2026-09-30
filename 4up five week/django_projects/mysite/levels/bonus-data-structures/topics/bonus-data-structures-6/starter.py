# 沿用關卡 2 的 Stack 類別（此處提供完整實作，方便本關卡獨立使用）
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        """移除並回傳堆疊頂端的元素，若堆疊為空則回傳 None"""
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """回傳堆疊頂端的元素但不移除，若堆疊為空則回傳 None"""
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0


class QueueUsingStacks:
    def __init__(self):
        self.stack_in = Stack()
        self.stack_out = Stack()

    def enqueue(self, item):
        # TODO: 請完成
        pass

    def dequeue(self):
        # TODO: 請完成
        pass