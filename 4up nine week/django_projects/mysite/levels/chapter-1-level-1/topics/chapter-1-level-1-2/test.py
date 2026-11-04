# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-1-2', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i, (name,age,weight) in enumerate([('小華',10,32.5),('大明',25,68.0),('小美',8,24.3)],1):
    observe(f'case{i}', introduce(f'{name}_{user_id}', age+user_id%10, weight+user_id%10))
