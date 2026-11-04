# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-10', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

root = None
for x in [8,3,10,1,6,14,4,7]:
    root = insert(root,x+user_id)
root = delete_node(root,3+user_id)
observe('two_children',inorder_values(root))
root = delete_node(root,14+user_id)
observe('leaf',inorder_values(root))
