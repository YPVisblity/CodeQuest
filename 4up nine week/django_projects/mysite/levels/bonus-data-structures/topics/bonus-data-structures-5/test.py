# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('bonus-data-structures-5', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

q = Queue()
q.enqueue(1+user_id)
q.enqueue(2+user_id)
observe('peek',q.peek())
observe('dequeue1',q.dequeue())
observe('dequeue2',q.dequeue())
observe('empty',q.is_empty())
observe('print_jobs',simulate_print_jobs([f'報告_{user_id}.pdf',f'作業_{user_id}.pdf',f'考卷_{user_id}.pdf']))
