# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-4', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

offset = user_id%20
a,b,c = [chr(65+offset+i) for i in range(3)]
observe('parentheses',infix_to_postfix(f'({a}+{b})*{c}'))
observe('precedence',infix_to_postfix(f'{a}+{b}*{c}'))
