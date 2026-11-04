# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

sll = SinglyLinkedList()
for x in [10,20,30]:
    sll.append(x+user_id)
observe('append',sll.to_list())
sll.insert_at(1,15+user_id)
observe('insert',sll.to_list())
sll.delete_by_value(15+user_id)
observe('delete',sll.to_list())
