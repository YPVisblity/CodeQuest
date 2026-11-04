# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-1-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i, pair in enumerate([(26+user_id,6+user_id),(10+user_id,3+user_id),(7+user_id,8+user_id),(5+user_id,0),(5+user_id,-3-user_id),(0,6+user_id)], 1):
    observe(f'case{i}', value(*pair))
