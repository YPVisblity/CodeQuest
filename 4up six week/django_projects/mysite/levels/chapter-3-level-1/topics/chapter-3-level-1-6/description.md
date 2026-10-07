請使用 Matplotlib 畫出一天時間分配的圓餅圖。

請完成 `create_pie_chart(activity, hours)` 函式：

1. 使用 `ax.pie(hours, labels=activity)` 畫出圓餅圖。
2. 將每個活動名稱顯示為圓餅圖的分類標籤。
3. 將圖表標題設定為「一天時間分配」。
4. 回傳畫圖使用的 `ax`（Axes）物件。

函式必須使用傳入的 `activity` 和 `hours` 繪圖，不可以將活動名稱、時間或區塊數量寫死在函式中。

例如：

- `activity = ["睡覺", "上課", "寫作業", "休閒"]`
- `hours = [8, 6, 4, 6]`

圖表應顯示四個區塊。每個區塊的標籤與大小比例，應分別依照 `activity` 和 `hours` 決定。
