import os

# 案例1：檔案不存在
result1 = read_score("不存在的檔案_xyz.txt")

# 案例2：檔案內容不是數字
bad_path = "temp_bad_score.txt"
with open(bad_path, "w") as f:
    f.write("abc")
result2 = read_score(bad_path)
os.remove(bad_path)
del bad_path

# 案例3：正常讀取
good_path = "temp_good_score.txt"
with open(good_path, "w") as f:
    f.write("6464")
result3 = read_score(good_path)
os.remove(good_path)
del good_path

# 案例4：另一個正常檔案（防止把分數寫死）
good_path2 = "temp_good_score2.txt"
with open(good_path2, "w") as f:
    f.write("87")
result4 = read_score(good_path2)
os.remove(good_path2)
del good_path2