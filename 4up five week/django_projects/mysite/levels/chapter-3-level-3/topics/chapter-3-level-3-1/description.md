辦公室環境監測系統會定時從感測器 API 取得溫度、濕度資料，
但今天系統出現異常，部分感測器回傳了空值（None），
AI 寫的資料清洗函式沒有處理這個情況，導致後續計算出錯。

請完成 clean_sensor_data(readings) 函式：
輸入是一個 list，每個元素是 dict，格式為 sensor（感測器名稱）和 value（數值或 None）
請過濾掉 value 為 None 的項目
回傳過濾後的 list，保留原始順序

例如輸入 溫度A:25.3、溫度B:None、濕度A:60
應回傳 溫度A:25.3、濕度A:60（溫度B 被過濾掉）
