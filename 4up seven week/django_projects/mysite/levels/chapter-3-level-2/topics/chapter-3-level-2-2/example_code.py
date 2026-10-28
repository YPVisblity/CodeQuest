# 範例：AI 寫的批次驗證程式碼（有Bug，僅供參考，勿直接使用）
def buggy_verify_video_library(file_list):
    total = len(file_list)
    success = 0
    failed = []
    for f in file_list:
        result = verify_download(f)
        if result:   # Bug：字串只要不是空字串就是True，連"Error:..."也算True
            success += 1
        else:
            failed.append(f["filename"])
    return {"total": total, "success": success, "failed": failed}

# 試著執行看看會發生什麼事：
report = buggy_verify_video_library([
    {"filename": "lesson01.mp4", "size": 15420, "checksum_valid": True},
    {"filename": "lesson02.txt", "size": 5000, "checksum_valid": True},
])
print("AI的統計報告：", report)
print("但 lesson02.txt 明明格式錯誤，卻被算進success裡")
