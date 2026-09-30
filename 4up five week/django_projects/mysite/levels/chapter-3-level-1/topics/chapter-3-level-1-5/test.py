# 第一組測試資料
result_ax = create_scatter_plot(
    [150, 160, 165, 170, 180],
    [45, 55, 60, 68, 75],
)

count1 = sum(
    len(collection.get_offsets())
    for collection in result_ax.collections
)
points1 = []
for collection in result_ax.collections:
    points1.extend(
        tuple(point)
        for point in collection.get_offsets().tolist()
    )

title_result = result_ax.get_title()
xlabel_result = result_ax.get_xlabel()
ylabel_result = result_ax.get_ylabel()

# 第二組測試資料，用來檢查資料是否寫死
result_ax2 = create_scatter_plot(
    [155, 175],
    [48, 72],
)

count2 = sum(
    len(collection.get_offsets())
    for collection in result_ax2.collections
)
points2 = []
for collection in result_ax2.collections:
    points2.extend(
        tuple(point)
        for point in collection.get_offsets().tolist()
    )
