# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-3-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(a,b) in enumerate([([[1,2],[3,4]],[[5,6],[7,8]]),([[2,1],[0,3]],[[1,4],[5,2]])],1):
    a = [[x+user_id for x in row] for row in a]
    b = [[x+user_id for x in row] for row in b]
    observe(f'case{i}', matrix_add(a,b))
