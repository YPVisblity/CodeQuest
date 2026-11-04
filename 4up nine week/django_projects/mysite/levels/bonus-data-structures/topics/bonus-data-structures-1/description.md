請完成下方 `SinglyLinkedList` 類別中標記 `# TODO` 的方法：

1. `append(data)`：在串列「尾端」新增一個節點
2. `insert_at(index, data)`：在指定索引位置插入一個節點（index 從 0 開始）。若 index 為負數或超出串列長度，請 raise IndexError
3. `delete_by_value(data)`：刪除第一個資料值等於 data 的節點，若找不到則不做任何事
4. `to_list()`：回傳一個 Python list，內容為串列中所有節點的資料，方便測試與除錯

完成後執行下方的自我檢查（assert），全部通過即代表本關卡練習任務完成。

### 個人化測試
系統會依登入使用者的資料庫 ID 調整測資；請依函式收到的參數計算，不要把範例答案寫死。函式名稱與參數不變，學生不需要自行取得 ID。零值、負數、空資料及錯誤格式等測試仍會保留。
