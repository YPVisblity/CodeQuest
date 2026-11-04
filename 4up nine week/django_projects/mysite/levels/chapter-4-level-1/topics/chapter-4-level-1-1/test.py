# ID 測資：std_id3n 由後端提供；直接開啟 Notebook 時可用 0 示範。
import pybryt
from copy import deepcopy as _id_copy
user_id = int(std_id3n)
pybryt.set_initial_conditions({"cq_user_id": user_id})
_id_observations = {}

def observe(checkpoint, value):
    signature = ('chapter-4-level-1-1', checkpoint, user_id, _id_copy(value))
    _id_observations[checkpoint] = signature
    return signature

import cv2
import numpy as np
delta = user_id%30
image = np.zeros((120+delta,160+delta,3),dtype=np.uint8)
cv2.rectangle(image,(20,20),(70+delta,80),(255,255,255),-1)
cv2.circle(image,(120,60),15+user_id%11,(255,255,255),-1)
gray,binary,contour = draw_image_contours(image)
observe('gray',(gray.shape,gray.ndim,int(gray.sum())))
observe('binary',(binary.shape,tuple(int(x) for x in np.unique(binary)),int(np.count_nonzero(binary))))
red = (contour[:,:,0]==0)&(contour[:,:,1]==0)&(contour[:,:,2]==255)
observe('contours',(contour.shape,int(np.count_nonzero(red))))
