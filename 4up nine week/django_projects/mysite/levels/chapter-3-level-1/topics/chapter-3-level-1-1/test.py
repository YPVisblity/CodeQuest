# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-1-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(months,values) in enumerate([([1,2,3,4,5,6],[100,120,90,150,200,180]),([1,2,3],[50,80,60])],1):
    ax = plot_investment(months,[x+user_id for x in values])
    observe(f'xlim{i}',tuple(float(x) for x in ax.get_xlim()))
    observe(f'ylim{i}',tuple(float(x) for x in ax.get_ylim()))
