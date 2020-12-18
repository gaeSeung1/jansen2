from __future__ import print_function
import numpy as np
import cv2

# 같은 디렉토리 내의 "cat.jpg"라는 이미지 불러와 보여주기
image = cv2.imread("1218153749.jpg")
#cv2.imshow("Original", image)

# RGB 영상은 [0,255] 범위에 해당하는 픽셀이 존재, 우리가 생각하는 연산과 다름.
# 연산 후 0보다 작은 것은 0으로, 255보다 큰것은 255로 바꿔주게 됨.
print("max of 255: {}".format(cv2.add(np.uint8([200]), np.uint8([100]))))
print("min of 0: {}".format(cv2.subtract(np.uint8([50]), np.uint8([100]))))

# numpy는 255보다 커지면 0부터 다시 세기 시작, 0보다 작아지면 255부터 다시 세기 시작.
print("wrap around: {}".format(np.uint8([200]) + np.uint8([100])))
print("wrap around: {}".format(np.uint8([50]) - np.uint8([100])))

# 밝게하기(원본보다 100만큼 밝게(최대 255))
M = np.ones(image.shape, dtype = "uint8") * 20
added = cv2.add(image, M)
cv2.imshow("Added", added)

# 어둡게하기(원본보다 50만큼 어둡게(최대 255))
M = np.ones(image.shape, dtype = "uint8") * 50
subtracted = cv2.subtract(image, M)
#cv2.imshow("Subtracted", subtracted)
cv2.waitKey(0)
