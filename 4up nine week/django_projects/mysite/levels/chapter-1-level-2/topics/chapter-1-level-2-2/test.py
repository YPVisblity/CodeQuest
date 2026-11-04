# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-2-2', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

scores = [95,90,86,80,72,70,64,60,40,user_id%101,(user_id*7+13)%101]
observe('grades', [grade(s) for s in scores])
