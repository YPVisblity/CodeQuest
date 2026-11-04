# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-2-level-2-2', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory(prefix=f'cq_{user_id}_') as folder:
    base = Path(folder)
    observe('missing_file',read_score(str(base/'missing.txt')))
    bad = base/'bad.txt'
    bad.write_text('abc',encoding='utf-8')
    observe('invalid_content',read_score(str(bad)))
    for i,number in enumerate([6464+user_id,87+user_id],1):
        good = base/f'good{i}.txt'
        good.write_text(str(number),encoding='utf-8')
        observe(f'valid_file{i}',read_score(str(good)))
