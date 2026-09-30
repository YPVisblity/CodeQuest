# 範例：AI 寫的平均值計算（有Bug，僅供參考，勿直接使用）
def buggy_average(readings):
    valid = [r["value"] for r in readings if r["value"] is not None]
    return sum(valid) / len(valid)   # 若 valid 是空list，這裡會直接除以零

# 試著執行看看會發生什麼事：
try:
    buggy_average([{"sensor": "A","value": None}])
except ZeroDivisionError as e:
    print("AI的程式碼出錯了：", e)
