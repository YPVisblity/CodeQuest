result_ax = plot_compare_investment(
    [1, 2, 3, 4],
    [100, 120, 90, 150],
    [80, 85, 95, 110],
)
legend1 = result_ax.get_legend()
legend_labels1 = [t.get_text() for t in legend1.get_texts()] if legend1 else []
line_count1 = len(result_ax.get_lines())

result_ax2 = plot_compare_investment(
    [1, 2, 3],
    [50, 60, 55],
    [70, 65, 80],
)
legend2 = result_ax2.get_legend()
legend_labels2 = [t.get_text() for t in legend2.get_texts()] if legend2 else []
