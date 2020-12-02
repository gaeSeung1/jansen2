PORT = 6000
host = 'gaeseung.local'
#host = 'localhost'

# 0 : main, 1 : main+streaming
switch = 0

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import ar_markers
from Time import Time
import threading
from queue import Queue
from http.client import HTTPConnection
import RPi.GPIO as GPIO
from decision import *

#motor init
GPIO.setmode(GPIO.BCM)
motor11=23
motor12=24
motor21=27
motor22=17
pwm1=25
pwm2=22

GPIO.setup(motor11,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(motor12,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(motor21,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(motor22,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(pwm1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(pwm2,GPIO.OUT,initial=GPIO.LOW)

p1=GPIO.PWM(pwm1,100)
p2=GPIO.PWM(pwm2,100)

p1.start(0)
p2.start(0)

# ultrasonic init
GPIO_TRIGGER = 14
GPIO_ECHO    = 15
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)
GPIO.output(GPIO_TRIGGER, False)

#motor action init
#speed = 50
HALF=0
MOTOR_SPEEDS = {
    "q": (1, 1), "w": (1, 1), "e": (1, 1),
    "a": (-1, 1), "s": (0, 0), "d": (1, -1),
    "z": (-HALF, -1), "x": (-1, -1), "c": (-1, -HALF),
}

# socket HTTPConnection
conn = HTTPConnection(f"{host}:{PORT}")

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

def cascade(img):
    face_cascade = cv2.CascadeClassifier('./cascade.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    objs = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in objs:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    return objs

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

def motor(action, m):

    if action == 's':
        direction = 'stop'
        speed = 0
        pw1 = min(speed * MOTOR_SPEEDS[action][0], 100)
        pw2 = min(speed * MOTOR_SPEEDS[action][1], 100)

    elif action == 'q':
        direction = 'left'
        speed = 50
        pw1 = max(speed * MOTOR_SPEEDS[action][1] - abs(m)*30, -100)
        pw2 = min(speed * MOTOR_SPEEDS[action][0] + abs(m)*50, 100)
        
    elif action == 'e':
        direction = 'right'
        speed = 50
        pw1 = min(speed * MOTOR_SPEEDS[action][0] + abs(m)*50, 100)
        pw2 = max(speed * MOTOR_SPEEDS[action][1] - abs(m)*30, -100)

    elif action == 'a':
        direction = 'spin left'
        speed = 50
        pw1 = min(speed * MOTOR_SPEEDS[action][0], 100)
        pw2 = min(speed * MOTOR_SPEEDS[action][1], 100)

    elif action == 'd':
        direction = 'spin right'
        speed = 50
        pw1 = min(speed * MOTOR_SPEEDS[action][0], 100)
        pw2 = min(speed * MOTOR_SPEEDS[action][1], 100)

    elif action == 'w':
        direction = 'forward'
        speed = 50
        pw1 = min(speed * MOTOR_SPEEDS[action][0], 100)
        pw2 = min(speed * MOTOR_SPEEDS[action][1], 100)

    elif action == 'x':
        direction = 'backward'
        speed = 40
        pw1 = min(speed * MOTOR_SPEEDS[action][0], 100)
        pw2 = min(speed * MOTOR_SPEEDS[action][1], 100)

    if pw1>0:
        GPIO.output(motor11,GPIO.HIGH)
        GPIO.output(motor12,GPIO.LOW)
    elif pw1<0:
        GPIO.output(motor11,GPIO.LOW)
        GPIO.output(motor12,GPIO.HIGH)
    else:
        GPIO.output(motor11,GPIO.LOW)
        GPIO.output(motor12,GPIO.LOW)
    if pw2>0:
        GPIO.output(motor21,GPIO.HIGH)
        GPIO.output(motor22,GPIO.LOW)
    elif pw2<0:
        GPIO.output(motor21,GPIO.LOW)
        GPIO.output(motor22,GPIO.HIGH)
    else:
        GPIO.output(motor21,GPIO.LOW)
        GPIO.output(motor22,GPIO.LOW)
    p1.ChangeDutyCycle(abs(pw1))
    p2.ChangeDutyCycle(abs(pw2))
    print(pw1,pw2)
    return direction
    
def ultrasonic():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()
    timeOut = start

    while GPIO.input(GPIO_ECHO)==0:
        start = time.time()
        if time.time()-timeOut > 0.012:
            return -1

    while GPIO.input(GPIO_ECHO)==1:
        if time.time()-start > 0.012:
            return -1
        stop = time.time()

    elapsed = stop-start
    distance = (elapsed * 34300)/2

    return distance


def main(q):
    #for capture every second
    checktimeBefore = int(time.strftime('%S'))

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text

        image = frame.array

        #undistort
        undistorted_image = undistort(image)


#--------------motor control--------------

        #decision (action, round(m,4), forward, left_line, right_line, center, direction)
        masked_image=select_white(undistorted_image,160)
        result=set_path3(masked_image)

        #line marker
        line = []
        #right        
        for j in range(result[2]):
            left_coord = (+result[5]+1+result[3][j], 239-j)
            line.append(left_coord)
            undistorted_image = cv2.line(undistorted_image, left_coord, left_coord,(0,255,0), 4)
        
        #left
        for j in range(result[2]):
            right_coord = (result[5]+1-result[4][j], 239-j)
            line.append(right_coord)
            undistorted_image = cv2.line(undistorted_image, right_coord, right_coord,(0,255,0), 4)
        
        #slope
        try:
            undistorted_image = cv2.line(undistorted_image, result[6][0], result[6][1],(0,0,255), 4)
        except:
            pass    
        #decision motor
        direction = motor(result[0], result[1])
        if result[0] == 'a' or result[0] == 'd':
            time.sleep(0.5)
        print(result[2])
        
        #e-stop
        if result[2] > 230:
            motor('s',0)
#----------------------------

        #ultrasonic
        ultra = ultrasonic()
        if ultra > 0 and ultra < 12:
            #print('stop')
            direction = motor('s',0)
            print(ultra)

        #cascade
#        cas = len(cascade(undistorted_image))
#        if cas != 0:
#            direction = motor('s')
            
        #AR marker
        markers = ar_markers.detect_markers(undistorted_image)
        for marker in markers:
            if marker.id == 114:
                direction = motor('q',result[1])
            elif marker.id == 922:
                direction = motor('e',result[1])
            elif marker.id == 2537:
                direction = motor('s',0)               
            marker.highlite_marker(undistorted_image)
#----------------------------
        #putText
        try:
            #slope
            cv2.putText(undistorted_image,'m = '+str(result[1]), (10,20),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1) 
            #direction
            cv2.putText(undistorted_image, direction, (10,40),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1) 
        except:
            pass
#----------------------------
        # show the frame
        cv2.imshow("Frame", undistorted_image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)

        #Threading
        if switch == 1:
            evt = threading.Event()
            qdata = undistorted_image
            q.put((qdata, evt))

        # q : break, tap : capture
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


if __name__ == "__main__":
    q = Queue()
    thread_one = threading.Thread(target=main, args=(q,))
    thread_two = threading.Thread(target=streaming, args=(q,))
    thread_two.daemon = True

    thread_one.start()
    if switch == 1:
        thread_two.start()

    q.join()


