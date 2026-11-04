class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        """將元素加入堆疊頂端"""
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
        """檢查堆疊是否為空，回傳布林值"""
        return len(self.items) == 0

def infix_to_postfix(expression):
    """將中序表達式轉換為後序表達式，只需處理 + - * / 與括號"""
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    stack = Stack()
    output = []
    # TODO: 請完成這個函式
    return "".join(output)