# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-2-3', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

years = [2000,1900,2024,2023,2100,1600,2000+user_id,2001+user_id]
observe('leap_years', [is_leap_year(y) for y in years])
