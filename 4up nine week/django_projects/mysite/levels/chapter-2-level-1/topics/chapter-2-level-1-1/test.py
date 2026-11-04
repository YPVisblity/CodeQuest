# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-2-level-1-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

score = user_id
history = [update_score(points) for points in [10,5,-8,0]]
observe('first_history',tuple(history+[score]))
score = 100+user_id
history = [update_score(points) for points in [-25,10]]
observe('second_history',tuple(history+[score]))
