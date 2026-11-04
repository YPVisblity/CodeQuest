# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-3-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

groups = [
 [{'sensor':f'A_{user_id}','value':20+user_id},{'sensor':f'B_{user_id}','value':None},{'sensor':f'C_{user_id}','value':30+user_id}],
 [{'sensor':f'X_{user_id}','value':None},{'sensor':f'Y_{user_id}','value':None}],
 [{'sensor':f'Z1_{user_id}','value':0},{'sensor':f'Z2_{user_id}','value':100+user_id}],
]
for i,readings in enumerate(groups,1):
    observe(f'case{i}',clean_sensor_data(readings))
