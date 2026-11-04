# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-2-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

# 同步縮放身高和體重，保留正常、過輕、過重三種分類。
scale = 1 + (user_id % 20) / 100
for i,(height,weight) in enumerate([(1.78,70),(1.60,40),(1.60,80)],1):
    observe(f'case{i}', basic(height*scale,weight*scale*scale))
