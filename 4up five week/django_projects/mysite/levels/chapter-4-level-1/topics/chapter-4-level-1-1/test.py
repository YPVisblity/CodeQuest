import cv2
import numpy as np

test_image1 = np.zeros((120, 160, 3), dtype=np.uint8)
cv2.rectangle(test_image1, (20, 20), (70, 80), (255, 255, 255), -1)
cv2.circle(test_image1, (120, 60), 25, (255, 255, 255), -1)

gray1, binary1, contour1 = draw_image_contours(test_image1)

gray_signature1 = (
    gray1.shape,
    gray1.ndim,
    int(gray1.sum()),
)
binary_signature1 = (
    binary1.shape,
    tuple(int(value) for value in np.unique(binary1)),
    int(np.count_nonzero(binary1)),
)
red_mask1 = (
    (contour1[:, :, 0] == 0)
    & (contour1[:, :, 1] == 0)
    & (contour1[:, :, 2] == 255)
)
contour_signature1 = (
    contour1.shape,
    int(np.count_nonzero(red_mask1)),
)
