# 在這裡寫程式
import math

def basic(height, weight):
    bmi = weight / math.pow(height, 2)
    if bmi < 18.5:
        print("過輕")
    # TODO: 請完成剩下的判斷式（正常、過重）
