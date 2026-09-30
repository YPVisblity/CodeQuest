# 第一組測試資料
result_ax = create_bar_chart(
    ["Apple", "Banana", "Orange", "Grape"],
    [30, 45, 25, 40],
)

count1 = len(result_ax.patches)
price_result1 = [bar.get_height() for bar in result_ax.patches]
fruit_result1 = [label.get_text() for label in result_ax.get_xticklabels()]
title_result = result_ax.get_title()
xlabel_result = result_ax.get_xlabel()
ylabel_result = result_ax.get_ylabel()

# 第二組測試資料，用來檢查資料是否寫死
result_ax2 = create_bar_chart(
    ["Mango", "Peach"],
    [50, 35],
)

count2 = len(result_ax2.patches)
price_result2 = [bar.get_height() for bar in result_ax2.patches]
fruit_result2 = [label.get_text() for label in result_ax2.get_xticklabels()]
