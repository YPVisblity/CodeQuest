教育訓練影片庫遭病毒感染，下載功能受到影響，
有些影片下載後檔案是損毀的，但 AI 寫的下載模組沒有檢查這件事，
導致損毀的影片也被當成下載成功。

請完成 verify_download(file_info) 函式：
輸入是一個 dict，包含 filename（檔名）、size（檔案大小，單位KB）、checksum_valid（雜湊碼是否正確，布林值）
若 filename 不是以 .mp4 結尾，回傳 "Error:格式錯誤"
若 size 小於等於 0，回傳 "Error:檔案損毀"
若 checksum_valid 是 False，回傳 "Error:校驗失敗"
若以上都通過，回傳 "OK:下載成功"

若同時有多個條件不符合，請依照「格式錯誤 > 檔案損毀 > 校驗失敗」的優先順序，只回傳最優先的那一個錯誤
（例如格式錯誤又同時檔案損毀，應回傳 "Error:格式錯誤"）

例如輸入 filename="lesson01.mp4", size=15420, checksum_valid=True
應回傳 "OK:下載成功"
