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
from sys import argv
from http.client import HTTPConnection
import json

PORT = 6000
#host = 'gaeseung.local'
host = 'localhost'
conn = HTTPConnection(f"{host}:{PORT}")
# 0 : main, 1 : capture every second, 2 : main+streaming
switch = 0

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


def UploadNumpy(img):
    result, img = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not result:
        raise Exception('Image encode error')

    conn.request('POST', '/', img.tobytes(), {
        "X-Client2Server" : "123"
    })
    res = conn.getresponse()

def Uploadkeyboard(q):
    try:
        conn.request("GET", "/")
    except ConnectionRefusedError as error:
        print(error)
        sleep(1)
        
    res = conn.getresponse()
    while True:                     
        #key read
        chunk = res.readline()
        if (chunk == b'\n'): continue
        if (not chunk): break

        chunk = chunk[:-1].decode()
        data = json.loads(chunk)
        print(Time(), data)
        action = data['action']
        if switch == 3:
            evt = threading.Event()
            qdata = data
            q.put((qdata, evt))



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
        checktime = int(time.strftime('%S'))
        if checktime - checktimeBefore >=1 and switch == 1:
            captured(undistorted_image)      
            checktimeBefore = checktime

        # Threading
        if switch == 2:
            evt = threading.Event()
            qdata = undistorted_image
            q.put((qdata, evt))

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
        elif key == ord("\t"):
            captured(undistorted_image)

def streaming(q):
    while True:
        qdata, evt = q.get()
        UploadNumpy(qdata)
        evt.set()
        q.task_done()

q = Queue()

thread_one = threading.Thread(target=main, args=(q,))
thread_two = threading.Thread(target=streaming, args=(q,))
#thread_three = threading.Thread(target=Uploadkeyboard, args=(q,))
thread_two.daemon = True
#thread_three.daemon = True

thread_one.start()
if switch == 2:
    thread_two.start()
#thread_three.start()

q.join()


