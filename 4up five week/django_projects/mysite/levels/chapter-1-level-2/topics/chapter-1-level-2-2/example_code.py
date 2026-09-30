def basic(height,weight):
    bmi= weight/pow(height,2)
    if (bmi < 18.5):
        return "過輕"
    elif (bmi >24):
        return "過重"
    else:
        return "正常"