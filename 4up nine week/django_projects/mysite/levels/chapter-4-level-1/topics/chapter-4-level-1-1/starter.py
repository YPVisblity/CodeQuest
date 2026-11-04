import cv2

# 在這裡寫程式
def draw_image_contours(image):
    # 1. 將圖片轉為灰階
    gray_image = None

    # 2. 使用 Otsu 方法進行二值化
    binary_image = None

    # 3. 尋找全部輪廓
    contours = []

    # 4. 複製原圖並繪製紅色輪廓
    contour_image = None

    return gray_image, binary_image, contour_image
