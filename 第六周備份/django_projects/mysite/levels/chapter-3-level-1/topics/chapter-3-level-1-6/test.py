# 第一組測試資料
result_ax = create_pie_chart(
    ["睡覺", "上課", "寫作業", "休閒"],
    [8, 6, 4, 6],
)

count1 = len(result_ax.patches)
labels1 = [
    text.get_text()
    for text in result_ax.texts
    if text.get_text()
]
ratios1 = [
    round((wedge.theta2 - wedge.theta1) / 360, 6)
    for wedge in result_ax.patches
]
title_result = result_ax.get_title()

# 第二組測試資料，用來檢查資料是否寫死
result_ax2 = create_pie_chart(
    ["讀書", "運動"],
    [3, 1],
)

count2 = len(result_ax2.patches)
labels2 = [
    text.get_text()
    for text in result_ax2.texts
    if text.get_text()
]
ratios2 = [
    round((wedge.theta2 - wedge.theta1) / 360, 6)
    for wedge in result_ax2.patches
]
