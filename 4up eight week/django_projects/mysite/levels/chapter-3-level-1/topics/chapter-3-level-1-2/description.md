主管看了你修好的投資走勢圖很滿意，現在想同時比較「股票」和「基金」兩筆投資，
方便一眼看出哪個報酬比較好。

AI 幫忙把兩條線都畫在同一張圖上了，但主管反應完全看不出哪條線是股票、哪條線是基金，
因為 AI 忘記幫每條線加上標籤（label）跟圖例（legend）。

請完成 plot_compare_investment(months, stock_values, fund_values) 函式：
在同一張圖上畫兩條折線：股票（stock_values）跟基金（fund_values），都對應 months
畫股票線時要加上 label="股票"，畫基金線時要加上 label="基金"
呼叫 ax.legend() 讓圖例顯示出來
回傳畫圖用的 ax（Axes）物件

例如輸入 months=[1,2,3,4]、stock_values=[100,120,90,150]、fund_values=[80,85,95,110]
圖上應該要能看到兩條線，圖例分別標示「股票」與「基金」
