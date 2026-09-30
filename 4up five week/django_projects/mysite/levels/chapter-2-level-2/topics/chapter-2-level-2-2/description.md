請定義 read_score(filename)，讀取檔案內容並轉成整數分數回傳。

規則：
1. 若檔案不存在，回傳 "Error:找不到檔案"
2. 若檔案內容不是數字（無法轉成 int），回傳 "Error:格式錯誤"
3. 若讀取成功，回傳分數（int）

請使用 try/except 分別處理 FileNotFoundError 與 ValueError 兩種例外。