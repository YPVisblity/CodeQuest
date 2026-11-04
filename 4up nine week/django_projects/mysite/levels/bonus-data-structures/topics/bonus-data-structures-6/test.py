# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-6', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

qs = QueueUsingStacks()
observe('stack_in_type',isinstance(qs.stack_in,Stack))
observe('stack_out_type',isinstance(qs.stack_out,Stack))
for x in [1,2,3]:
    qs.enqueue(x+user_id)
observe('lazy_transfer',qs.stack_out.is_empty())
observe('dequeue1',qs.dequeue())
observe('transferred_all',qs.stack_in.is_empty())
qs.enqueue(4+user_id)
for i in range(2,5):
    observe(f'dequeue{i}',qs.dequeue())
