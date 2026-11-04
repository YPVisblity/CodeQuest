廣播系統需要把文字公告轉換成繁體中文語音，並儲存為 MP3 檔案。

請完成 create_voice_announcement(text, output_path, tts_factory) 函式：

1. 若 text 不是字串、內容為空或只有空白，回傳 "Error:文字不可為空"。
2. 若 output_path 不是字串或不是以 .mp3 結尾，回傳 "Error:檔案格式錯誤"。
3. 移除文字前後的空白。
4. 呼叫 tts_factory(text=處理後的文字, lang="zh-TW") 建立語音物件。
5. 呼叫語音物件的 save(output_path) 儲存檔案。
6. 成功後回傳 "語音建立完成"。

實際使用時，tts_factory 可以傳入 gTTS；自動評測時會使用不需連網的測試物件。

### 個人化測試
系統會依登入使用者的資料庫 ID 調整測資；請依函式收到的參數計算，不要把範例答案寫死。函式名稱與參數不變，學生不需要自行取得 ID。零值、負數、空資料及錯誤格式等測試仍會保留。
