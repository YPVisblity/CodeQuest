# 範例：處理單一例外（已完成，供參考）
def safe_open(filename):
    try:
        with open(filename) as f:
            return f.read()
    except FileNotFoundError:
        return "找不到這個檔案"

print(safe_open("不存在的檔案.txt"))