qs = QueueUsingStacks()

# 結構檢查：必須是用提供的 Stack，不能被繞過
assert isinstance(qs.stack_in, Stack), "stack_in 必須是 Stack 的實例"
assert isinstance(qs.stack_out, Stack), "stack_out 必須是 Stack 的實例"

qs.enqueue(1)
qs.enqueue(2)
qs.enqueue(3)

# 進階結構檢查：enqueue 之後元素應該都還在 stack_in，
# stack_out 應該是空的（還沒發生轉移），確保不是每次都硬轉移
assert qs.stack_out.is_empty(), "尚未 dequeue 前 stack_out 應為空（延遲轉移）"

r1 = qs.dequeue()
r2_precheck = qs.stack_in.is_empty()  # 轉移後 stack_in 應該被清空
qs.enqueue(4)
r2 = qs.dequeue()
r3 = qs.dequeue()
r4 = qs.dequeue()