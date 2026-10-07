一張圖片中藏有多個物體，請使用 OpenCV 找出物體輪廓，並把輪廓標示在原圖上。

請完成 draw_image_contours(image) 函式：

1. 使用 cv2.cvtColor() 與 cv2.COLOR_BGR2GRAY 將 BGR 圖片轉成灰階圖片。
2. 使用 cv2.threshold() 將灰階圖片二值化，參數為 127、255，並結合 cv2.THRESH_BINARY 與 cv2.THRESH_OTSU。
3. 使用 cv2.findContours() 尋找輪廓，模式使用 cv2.RETR_LIST，近似方式使用 cv2.CHAIN_APPROX_SIMPLE。
4. 複製原始圖片，避免直接修改輸入圖片。
5. 使用 cv2.drawContours() 繪製全部輪廓，顏色為紅色 (0, 0, 255)，厚度為 2。
6. 依序回傳灰階圖片、二值圖片與繪製輪廓後的圖片。

回傳格式：

return gray_image, binary_image, contour_image

注意：評測時不需要使用 cv2.imshow()、cv2.waitKey() 或讀取外部圖片檔。
