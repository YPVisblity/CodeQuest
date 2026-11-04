# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-1-level-3-3', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,matrix in enumerate([[[1,8],[3,4]],[[-5,-2],[-9,-1]],[[7],[11],[6]]],1):
    matrix = [[x-user_id if x<0 else (x+user_id if x>0 else 0) for x in row] for row in matrix]
    observe(f'case{i}', matrix_max(matrix))
