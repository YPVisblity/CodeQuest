class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        """加入佇列尾端"""
        self.items.append(item)

    def dequeue(self):
        """移除並回傳佇列前端元素，若為空則回傳 None"""
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def peek(self):
        """查看佇列前端元素，若為空則回傳 None"""
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        """判斷佇列是否為空"""
        return len(self.items) == 0

def simulate_print_jobs(jobs):
    q = Queue()
    result = []
    for job in jobs:
        q.enqueue(job)
    while True:
        if q.is_empty():
            break
        result.append(q.dequeue())
    return result