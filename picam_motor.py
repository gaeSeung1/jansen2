# 0 : main, 1 : capture every second
switch = 0

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
from Time import Time
import RPi.GPIO as GPIO
from detect import detect_markers

# motor init
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

# motor action init
speed = 70
HALF=0
MOTOR_SPEEDS = {
    ord("q"): (HALF, 1), ord("w"): (1, 1), ord("e"): (1, HALF),
    ord("a"): (-1, 1), ord("s"): (0, 0), ord("d"): (1, -1),
    ord("z"): (-HALF, -1), ord("x"): (-1, -1), ord("c"): (-1, -HALF),
}

print('Press "esc" to quit')

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

def motor(action):
    pw1 = speed * MOTOR_SPEEDS[action][0]
    pw2 = speed * MOTOR_SPEEDS[action][1]
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
    if action == ord('s'):
        print('stop')
    elif action == ord('a'):
        print('left')
    elif action == ord('d'):
        print('right')


def main():
    motor_key = 115
    #for capture every second
    checktimeBefore = int(time.strftime('%S'))

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text

        image = frame.array

        #undistort
        undistorted_image = undistort(image)

        #----motor control----

        #cascade
        cas = len(cascade(undistorted_image))
        if cas != 0:
            print(cas)
            #motor('s')

        #AR marker
        distance = detect_markers(undistorted_image)[1]
        markers = detect_markers(undistorted_image)[0]
        
        for marker in markers:
            marker.highlite_marker(undistorted_image)
            if distance > 60:
                print("distance :", distance)
                if marker.id == 114:
                    print('left', marker.id)
                elif marker.id == 922:
                    print('right', marker.id)
                elif marker.id == 2537:
                    print('stop', marker.id)              
                

        # show the frame
        cv2.imshow("Frame", undistorted_image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)



        # 1 : capture negative images every second
        if switch == 1:
            checktime = int(time.strftime('%S'))
            if checktime - checktimeBefore >=1:
                captured(undistorted_image)      
                checktimeBefore = checktime
        print(key)
        if key == 27:
            break
        elif key == ord("\t"):
            captured(undistorted_image)
        elif key in MOTOR_SPEEDS:
            motor_key = key
            motor(motor_key)
        elif key == 255:
            motor(motor_key)
        elif key == 32: #space bar
            pass


main()