# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-1-3', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(days,temperatures) in enumerate([([1,2,3,4,5],[22,24,23,26,28]),([1,2,3],[18,21,20])],1):
    ax = create_plot(days,[x+user_id for x in temperatures])
    observe(f'count{i}',len(ax.lines))
    observe(f'data{i}',[(list(line.get_xdata()),list(line.get_ydata())) for line in ax.lines])
    observe(f'labels{i}',(ax.get_title(),ax.get_xlabel(),ax.get_ylabel()))
