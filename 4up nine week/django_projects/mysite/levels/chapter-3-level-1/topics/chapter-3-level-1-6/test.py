# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-1-6', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(activities,hours) in enumerate([(['睡覺','上課','寫作業','其他'],[8,6,4,6]),(['讀書','運動'],[3,1])],1):
    ax = create_pie_chart([f'{x}_{user_id}' for x in activities],[x+user_id for x in hours])
    observe(f'count{i}',len(ax.patches))
    observe(f'labels{i}',[t.get_text() for t in ax.texts if t.get_text()])
    observe(f'ratios{i}',[round(float(w.theta2-w.theta1)/360,6) for w in ax.patches])
    observe(f'title{i}',ax.get_title())
