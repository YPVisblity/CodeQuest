# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-9', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

bst_root = None
for x in [8,3,10,1,6,14]:
    bst_root = insert(bst_root,x+user_id)
for i,target in enumerate([6+user_id,14+user_id,100+user_id,user_id],1):
    observe(f'search{i}',search(bst_root,target))
