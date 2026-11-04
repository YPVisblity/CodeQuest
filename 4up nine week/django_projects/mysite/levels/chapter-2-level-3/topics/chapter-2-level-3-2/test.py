# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-2-level-3-2', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

html1 = f'<html><h2>第一篇_{user_id}</h2><p>忽略</p><h2>第二篇_{user_id}</h2><h2>第三篇_{user_id}</h2></html>'
html2 = f'<h1>忽略_{user_id}</h1><h2>唯一標題_{user_id}</h2>'
html3 = f'<p>沒有標題_{user_id}</p>'
for i,html in enumerate([html1,html2,html3],1):
    observe(f'case{i}',extract_titles(html))
