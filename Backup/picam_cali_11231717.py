# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
from matplotlib import pyplot as plt
import ar_markers
import ImageRW
from Time import Time
import threading
from queue import Queue


# You should replace these 3 lines with the output in calibration step
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

def cascade(img):
        face_cascade = cv2.CascadeClassifier('./cascade.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objs = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in objs:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        if objs != ():
            pass
            print('stop')

#undistort
def undistort(img):
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    return img


# capture frames from the camera
def main(q):

    #for capture every second
    checktimeBefore = int(time.strftime('%S'))

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text

        image = frame.array

        #undistort
        undistorted_image = undistort(image)

        #cascade
        cascade(undistorted_image)

        #AR marker
        markers = ar_markers.detect_markers(undistorted_image)
        for marker in markers:
            print('marker :', marker.id) #, marker.center)
            marker.highlite_marker(undistorted_image)

        # show the frame
        cv2.imshow("Frame", undistorted_image)
        key = cv2.waitKey(1) & 0xFF
        
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        # 1 : capture negative images every second
        switch = 0
        checktime = int(time.strftime('%S'))
        if checktime - checktimeBefore >=1 and switch == 1:
            captured(undistorted_image)      
            checktimeBefore = checktime

        # Threading
        evt = threading.Event()
        data = undistorted_image
        q.put((data, evt))

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
        elif key == ord("\t"):
            captured(undistorted_image)

def streaming(q):
    while True:
        data, evt = q.get()
        ImageRW.UploadNumpy(data)
        evt.set()
        q.task_done()
        
q = Queue()

thread_one = threading.Thread(target=main, args=(q,))
thread_two = threading.Thread(target=streaming, args=(q,))
#thread_one.daemon = True
thread_two.daemon = True

thread_one.start()
thread_two.start()

q.join()

