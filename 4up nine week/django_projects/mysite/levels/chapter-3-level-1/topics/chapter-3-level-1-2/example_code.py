# 範例：AI 寫的投資比較圖函式（有Bug，僅供參考，勿直接使用）
import matplotlib.pyplot as plt

def buggy_plot_compare(months,stock_values,fund_values):
    fig, ax = plt.subplots()
    ax.plot(months,stock_values)   # 忘記加 label
    ax.plot(months,fund_values)    # 忘記加 label
    return ax                       # 也忘記呼叫 ax.legend()

# 試著執行看看會發生什麼事：
ax = buggy_plot_compare([1, 2, 3],[100, 120, 90],[80, 85, 95])
print("圖例物件：",ax.get_legend())   # None，主管完全看不出哪條線是哪個投資
