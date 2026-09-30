請使用 Matplotlib 畫出溫度變化折線圖。

請完成 `create_plot(days, temperatures)` 函式：

1. 使用 `ax.plot(days, temperatures)` 畫出一條折線。
2. 將圖表標題設定為「溫差」。
3. 將 X 軸名稱設定為「天數」。
4. 將 Y 軸名稱設定為「溫度」。
5. 回傳畫圖使用的 `ax`（Axes）物件。

函式必須使用傳入的 `days` 和 `temperatures` 繪圖，不可以將天數或溫度資料寫死在函式中。

例如：

- `days = [1, 2, 3, 4, 5]`
- `temperatures = [22, 24, 23, 26, 28]`

圖表中應有一條折線，折線的座標應與傳入的資料相同。
