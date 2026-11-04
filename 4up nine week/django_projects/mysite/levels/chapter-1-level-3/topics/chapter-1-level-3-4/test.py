# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-3-4', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

observe('positive_difference',generate_arithmetic_sequence(2+user_id,3,5))
observe('negative_difference',generate_arithmetic_sequence(10+user_id,-4,4))
