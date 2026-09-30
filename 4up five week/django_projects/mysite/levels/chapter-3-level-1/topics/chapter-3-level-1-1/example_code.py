# 範例：AI 寫的投資走勢圖函式（有Bug，僅供參考，勿直接使用）
import matplotlib.pyplot as plt

def buggy_plot_investment(months,values):
    fig,ax = plt.subplots()
    ax.plot(months,values)
    ax.set_xlim(0, 12)      # 寫死的範圍，資料筆數不是12個月時就會跟實際資料對不起來
    ax.set_ylim(min(values), max(values))
    return ax

# 試著執行看看會發生什麼事：
ax = buggy_plot_investment([1, 2, 3, 4, 5, 6],[100, 120, 90, 150, 200, 180])
print("AI的程式碼算出來的X軸範圍：", ax.get_xlim())
print("但資料實際的月份範圍應該是：(1, 6)")
