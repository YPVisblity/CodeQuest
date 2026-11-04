# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-1-2', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

for i,(months,stocks,funds) in enumerate([([1,2,3,4],[100,120,90,150],[80,85,95,110]),([1,2,3],[50,60,55],[70,65,80])],1):
    ax = plot_compare_investment(months,[x+user_id for x in stocks],[x+user_id for x in funds])
    legend = ax.get_legend()
    observe(f'legend{i}',[t.get_text() for t in legend.get_texts()] if legend else [])
    observe(f'lines{i}',len(ax.lines))
    observe(f'line_data{i}',[(list(line.get_xdata()),list(line.get_ydata())) for line in ax.lines])
