s = Stack()
s.push(1)
s.push(2)
assert s.peek() == 2
assert s.pop() == 2
assert s.pop() == 1
assert s.is_empty() == True

result_1 = ("([{}])", is_balanced("([{}])"))
result_2 = ("([)]", is_balanced("([)]"))
result_3 = ("(()", is_balanced("(()"))
result_4 = ("", is_balanced(""))

print(result_1)
print(result_2)
print(result_3)
print(result_4)