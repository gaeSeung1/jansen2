import cv2
import numpy as np
import sys

# You should replace these 3 lines with the output in calibration step
DIM=(640, 480)
K=np.array([[263.5675051310029, 0.0, 333.54239147190935], [0.0, 265.3020184448716, 246.69004094668097], [0.0, 0.0, 1.0]])
D=np.array([[-0.06270506249774876], [0.059362967743236496], [-0.0734129632216966], [0.02527256070827014]])

def undistort(img_path):
    
    img = cv2.imread(img_path)
    print(img)
    print("1")
    print(img.shape[:2])
    h,w = img.shape[:2]
    print("2")
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    print("3")
    cv2.imshow("undistorted", undistorted_img)
    print(undistorted_img)
    cv2.waitKey(0)
    print("5")
    cv2.destroyAllWindows()

if __name__ == '__main__':

    undistort('output1.jpg')

#    for p in sys.argv[1:]:
#        undistort(p)