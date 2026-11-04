完成函式 `fetch_with_header(url)`：

1. 建立一個 `headers` 字典，裡面要有 `"User-Agent"` 這個 key，
   值要像一般瀏覽器（例如 Chrome）送出的字串。
2. 用 `requests.get(url, headers=headers)` 發送請求。
3. 回傳 response 的狀態碼 `status_code`。

## 提示
- 常見瀏覽器 User-Agent 格式（可以直接照抄）：
      Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
      (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

- headers 字典的 key 要精確是 `"User-Agent"`（第一個字母大小寫）。
- 這只是「表明自己是誰」的最基本做法，不是要繞過任何安全機制，
- 正式上線的爬蟲仍然要遵守目標網站的 robots.txt 與使用條款。

### 個人化測試
系統會依登入使用者的資料庫 ID 調整測資；請依函式收到的參數計算，不要把範例答案寫死。函式名稱與參數不變，學生不需要自行取得 ID。零值、負數、空資料及錯誤格式等測試仍會保留。
