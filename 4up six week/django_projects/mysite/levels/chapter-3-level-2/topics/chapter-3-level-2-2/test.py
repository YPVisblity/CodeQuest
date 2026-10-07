result1 = verify_video_library([
    {"filename": "lesson01.mp4", "size": 15420, "checksum_valid": True},
    {"filename": "lesson02.mp4", "size": 8300, "checksum_valid": True},
    {"filename": "lesson03.txt", "size": 5000, "checksum_valid": True},
    {"filename": "lesson04.mp4", "size": 0, "checksum_valid": True},
    {"filename": "lesson05.mp4", "size": 12000, "checksum_valid": False},
])

result2 = verify_video_library([
    {"filename": "a.mp4", "size": 100, "checksum_valid": True},
    {"filename": "b.mp4", "size": 200, "checksum_valid": True},
])

result3 = verify_video_library([])
