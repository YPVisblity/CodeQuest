AI 寫了一個更新玩家分數的函式，但函式在修改 score 時出現 UnboundLocalError，導致玩家無法獲得或扣除分數。

請修正 update_score(points) 函式：

1. score 是函式外的全域變數，初始值為 0。
2. 在函式內使用 global 宣告要修改全域 score。
3. 將 points 加到目前的 score。
4. points 可以是正數、0 或負數。
5. 回傳更新後的 score。
6. 每次呼叫都必須保留前一次更新後的分數。

例如依序執行：

update_score(10)
update_score(5)
update_score(-8)

應依序回傳 10、15、7，最後的全域 score 應為 7。
