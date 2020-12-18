from __future__ import print_function
import numpy as np
import cv2

# 같은 디렉토리 내의 "cat.jpg"라는 이미지 불러와 보여주기
image = cv2.imread("1218153749.jpg")


cv2.imshow("Added", image)

cv2.waitKey(0)
