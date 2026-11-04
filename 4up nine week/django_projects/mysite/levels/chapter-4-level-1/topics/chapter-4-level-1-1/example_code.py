# 範例：只示範讀取圖片與轉換灰階，不是本題完整答案
import cv2

image = cv2.imread("card.png")

if image is not None:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("原圖尺寸：", image.shape)
    print("灰階圖尺寸：", gray_image.shape)
else:
    print("找不到圖片")
