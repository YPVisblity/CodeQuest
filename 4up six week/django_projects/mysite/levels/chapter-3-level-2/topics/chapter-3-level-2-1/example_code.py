# 範例：AI 寫的下載驗證程式碼（有Bug，僅供參考，勿直接使用）
def buggy_verify(file_info):
    return "OK:下載成功"   # AI 完全沒做任何檢查，永遠回傳成功

# 試著執行看看會發生什麼事：
result = buggy_verify({"filename": "lesson01.txt", "size": 0, "checksum_valid": False})
print("AI的程式碼判定：", result)
print("但這個檔案明明格式錯誤、大小為0、校驗也失敗了")
