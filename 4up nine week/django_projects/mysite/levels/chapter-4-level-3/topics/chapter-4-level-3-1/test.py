# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-4-level-3-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

tts_record = {}
class FakeTTS:
    def __init__(self,text,lang):
        tts_record.update(text=text,lang=lang)
    def save(self,path):
        tts_record['saved_path'] = path
observe('valid',create_voice_announcement(f'  歡迎使用者{user_id}  ',f'welcome_{user_id}.mp3',FakeTTS))
observe('tts_parameters',dict(tts_record))
observe('empty',create_voice_announcement('   ',f'empty_{user_id}.mp3',FakeTTS))
observe('invalid_extension',create_voice_announcement(f'語音{user_id}',f'voice_{user_id}.wav',FakeTTS))
