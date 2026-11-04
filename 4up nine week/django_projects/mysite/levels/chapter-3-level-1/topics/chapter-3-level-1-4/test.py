# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-1-4', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(fruits,prices) in enumerate([(['Apple','Banana','Orange','Grape'],[30,45,25,40]),(['Mango','Peach'],[50,35])],1):
    ax = create_bar_chart([f'{x}_{user_id}' for x in fruits],[x+user_id for x in prices])
    observe(f'heights{i}',[float(bar.get_height()) for bar in ax.patches])
    observe(f'fruits{i}',[label.get_text() for label in ax.get_xticklabels()])
    observe(f'labels{i}',(ax.get_title(),ax.get_xlabel(),ax.get_ylabel()))
