# 範例：AI 寫的資料清洗程式碼（僅供參考）
def buggy_clean(readings):
    total = 0
    for r in readings:
        total += r["value"]   # 若 value 是 None，這裡會直接出錯
    return total

# 試著執行看看會發生什麼事：
try:
    buggy_clean([{"sensor":"A","value":10}, {"sensor":"B","value":None}])
except TypeError as e:
    print("AI的程式碼出錯了：",e)
