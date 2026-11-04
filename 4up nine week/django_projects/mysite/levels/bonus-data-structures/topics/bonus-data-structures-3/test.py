# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-3', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

s = Stack()
s.push(1+user_id)
s.push(2+user_id)
observe('peek',s.peek())
observe('pop1',s.pop())
observe('pop2',s.pop())
observe('empty',s.is_empty())
for i,expression in enumerate(['([{}])','([)]','(()',''],1):
    expression = expression*(1+user_id%3)
    observe(f'balanced{i}',is_balanced(expression))
