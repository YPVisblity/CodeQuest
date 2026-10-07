請使用 Matplotlib 畫出水果價格長條圖。

請完成 `create_bar_chart(fruit, price)` 函式：

1. 使用 `ax.bar(fruit, price)` 畫出長條圖。
2. 將圖表標題設定為「水果價格」。
3. 將 X 軸名稱設定為「水果」。
4. 將 Y 軸名稱設定為「價錢」。
5. 回傳畫圖使用的 `ax`（Axes）物件。

函式必須使用傳入的 `fruit` 和 `price` 繪圖，不可以將水果名稱、價格或長條數量寫死在函式中。

例如：

- `fruit = ["Apple", "Banana", "Orange", "Grape"]`
- `price = [30, 45, 25, 40]`

圖表應顯示四個長條，每個長條的分類和高度應與傳入的資料相同。
