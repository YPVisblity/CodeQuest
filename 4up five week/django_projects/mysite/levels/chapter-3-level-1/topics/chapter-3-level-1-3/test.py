# 第一組測試資料
result_ax = create_plot(
    [1, 2, 3, 4, 5],
    [22, 24, 23, 26, 28],
)

line_count1 = len(result_ax.lines)
line1 = result_ax.lines[0] if result_ax.lines else None
x_data1 = list(line1.get_xdata()) if line1 else []
y_data1 = list(line1.get_ydata()) if line1 else []
title_result = result_ax.get_title()
xlabel_result = result_ax.get_xlabel()
ylabel_result = result_ax.get_ylabel()

# 第二組測試資料，用來檢查資料是否寫死
result_ax2 = create_plot(
    [1, 2, 3],
    [18, 21, 20],
)

line_count2 = len(result_ax2.lines)
line2 = result_ax2.lines[0] if result_ax2.lines else None
x_data2 = list(line2.get_xdata()) if line2 else []
y_data2 = list(line2.get_ydata()) if line2 else []
