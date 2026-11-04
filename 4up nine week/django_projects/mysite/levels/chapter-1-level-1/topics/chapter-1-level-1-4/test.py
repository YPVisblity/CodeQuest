# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-1-4', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

observe('numbers', swap_values(1+user_id,2+user_id))
observe('negative', swap_values(100+user_id,-50-user_id))
observe('strings', swap_values(f'蘋果_{user_id}',f'香蕉_{user_id}'))
