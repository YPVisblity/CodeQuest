# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-1-5', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(heights,weights) in enumerate([([150,160,165,170,180],[45,55,60,68,75]),([155,175],[48,72])],1):
    ax = create_scatter_plot([x+user_id for x in heights],[x+user_id for x in weights])
    points = [tuple(point) for collection in ax.collections for point in collection.get_offsets().tolist()]
    observe(f'points{i}',points)
    observe(f'labels{i}',(ax.get_title(),ax.get_xlabel(),ax.get_ylabel()))
