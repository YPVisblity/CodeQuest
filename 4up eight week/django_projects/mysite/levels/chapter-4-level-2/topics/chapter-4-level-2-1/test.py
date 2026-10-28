import threading

play_record = []
barrier = threading.Barrier(2)

def fake_audio_player(path):
    try:
        barrier.wait(timeout=2)
        status = "同步"
    except threading.BrokenBarrierError:
        status = "未同步"

    play_record.append((
        "audio",
        path,
        threading.current_thread().name,
        status,
    ))

def fake_video_player(path):
    try:
        barrier.wait(timeout=2)
        status = "同步"
    except threading.BrokenBarrierError:
        status = "未同步"

    play_record.append((
        "video",
        path,
        threading.current_thread().name,
        status,
    ))

result1 = play_multimedia(
    "music.mp3",
    "movie.mp4",
    fake_audio_player,
    fake_video_player,
)
record1 = sorted(play_record)
