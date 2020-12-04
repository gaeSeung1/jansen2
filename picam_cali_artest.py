from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
from Time import Time
import threading
from queue import Queue
from http.client import HTTPConnection
import RPi.GPIO as GPIO
from decision import *
from detect import detect_markers

# Information of picam calibration 
DIM=(320, 240)
K=np.array([[132.13704662178574, 0.0, 166.0686598959872], [0.0, 133.16643727381444, 123.27563566060049], [0.0, 0.0, 1.0]])
D=np.array([[-0.07388057626177186], [0.037920859225125836], [-0.030619490583373123], [0.006819370459857302]])

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
#flip
camera.vflip = True
camera.hflip = True
#shutterspeed
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)
# allow the camera to warmup
time.sleep(0.1)

def captured(img):
    cv2.imwrite(time.strftime('%m%d%H%M%S')+'.jpg', img)


def undistort(img):
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return img

def main():

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text

        image = frame.array

        #undistort
        undistorted_image = undistort(image)

#--------------motor control--------------


        #AR marker
        markers = detect_markers(undistorted_image)[0]
        print(detect_markers(undistorted_image)[1])
        for marker in markers:
            marker.highlite_marker(undistorted_image)
    
        # show the frame
        cv2.imshow("Frame", undistorted_image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)

        # q : break, tap : capture
        if key == ord("q"):
            break
        elif key == ord("\t"):
            captured(undistorted_image)


if __name__ == "__main__":
    main()


