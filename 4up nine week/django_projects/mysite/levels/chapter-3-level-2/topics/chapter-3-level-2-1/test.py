# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-3-level-2-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

files = [
 {'filename':f'lesson01_{user_id}.mp4','size':15420+user_id,'checksum_valid':True},
 {'filename':f'lesson02_{user_id}.txt','size':8300+user_id,'checksum_valid':True},
 {'filename':f'lesson03_{user_id}.mp4','size':0,'checksum_valid':True},
 {'filename':f'lesson04_{user_id}.mp4','size':12000+user_id,'checksum_valid':False},
 {'filename':f'lesson05_{user_id}.txt','size':0,'checksum_valid':False},
]
for i,info in enumerate(files,1):
    observe(f'case{i}',verify_download(info))
