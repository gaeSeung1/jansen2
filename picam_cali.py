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
MOTOR_SPEEDS = {
    "q": (0, 1), "w": (1, 1), "e": (1, 0),
    "a": (-1, 1), "s": (0, 0), "d": (1, -1),
    "z": (0, -1), "x": (-1, -1), "c": (-1, 0),
}

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

def motor(action, m):
    if action == 's':
        direction = 'stop'
        speed = 0

    elif action == 'q':
        direction = 'left'
        speed = 50
        
    elif action == 'e':
        direction = 'right'
        speed = 50

    elif action == 'a':
        direction = 'spin left'
        speed = 70
        
    elif action == 'd':
        direction = 'spin right'
        speed = 70

    elif action == 'w':
        direction = 'forward'
        speed = 50

    elif action == 'x':
        direction = 'backward'
        speed = 40

    elif action == 'c':
        direction = 'backward-left'
        speed = 50

    elif action == 'z':
        direction = 'backward-right'
        speed = 50

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

    #print(pw1,pw2)
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


def main():
    #for capture every second
    checktimeBefore = int(time.strftime('%S'))
    stop_sign = 0
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
        line_left = []
        line_right = []
        for j in range(result[2]):
            #left
            left_coord = (result[5]+1-result[4][j], 239-j)
            line_left.append(left_coord)
            undistorted_image = cv2.line(undistorted_image, left_coord, left_coord,(0,255,0), 4)
            #right
            right_coord = (+result[5]+1+result[3][j], 239-j)
            line_right.append(right_coord)
            undistorted_image = cv2.line(undistorted_image, right_coord, right_coord,(0,255,0), 4)

        #slope
        try:
            undistorted_image = cv2.line(undistorted_image, result[6][0], result[6][1],(0,0,255), 4)
        except:
            pass    

        #straight
        if result[0] == 'w' and line_left != [] and line_right != []:
            straight_factor = 30
            if line_left[0][0] > straight_factor:
                result_direction = 'e'
            elif line_right[0][0] < 320-straight_factor:
                result_direction = 'q'
            else:
                result_direction = result[0]      
      
        else:
            result_direction = result[0]

        #motor ON!
        direction = motor(result_direction, result[1])
    
#----------------------------

        #ultrasonic
        ultra = ultrasonic()
        if ultra > 0 and ultra < 10:
            #print('stop')
            direction = motor('s',0)
            print(ultra)

        #cascade
        cas = len(cascade(undistorted_image))
        #if detected
        if cas != 0:
            if stop_sign == 2:
                direction = motor('s',result[1])
                print('stop sign')
                time.sleep(5)
            else:
                print('Non stop', stop_sign)
            stop_sign = stop_sign + 1

        #AR marker
        distance = detect_markers(undistorted_image)[1]
        markers = detect_markers(undistorted_image)[0]

        for marker in markers:
            #highlight
            marker.highlite_marker(undistorted_image)
            if distance > 40:
                print("distance :", distance)
                #left
                if marker.id == 114:
                    direction = motor('a',result[1])
                    print('left', marker.id)
                    time.sleep(0.2)
                #right
                elif marker.id == 922:
                    direction = motor('d',result[1])
                    print('right', marker.id)
                    time.sleep(0.2)
                #finish, stop
                elif marker.id == 2537:
                    direction = motor('s',0)
                    print('stop', marker.id)               
                    time.sleep(10)
            
            
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

        # q : break, tap : capture
        if key == ord("q"):
            break
        elif key == ord("\t"):
            captured(undistorted_image)


if __name__ == "__main__":
    main()


