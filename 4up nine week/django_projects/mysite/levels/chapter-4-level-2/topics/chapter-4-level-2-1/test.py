# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-4-level-2-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

import threading
play_record = []
barrier = threading.Barrier(2)
def fake_audio_player(path):
    try:
        barrier.wait(timeout=2)
        status = '同步'
    except threading.BrokenBarrierError:
        status = '不同步'
    play_record.append(('audio',path,threading.current_thread().name,status))
def fake_video_player(path):
    try:
        barrier.wait(timeout=2)
        status = '同步'
    except threading.BrokenBarrierError:
        status = '不同步'
    play_record.append(('video',path,threading.current_thread().name,status))
observe('result',play_multimedia(f'music_{user_id}.mp3',f'movie_{user_id}.mp4',fake_audio_player,fake_video_player))
observe('threads',sorted(play_record))
