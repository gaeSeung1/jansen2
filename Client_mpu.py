PORT = 6000

from http.client import HTTPConnection
import json
import time
import numpy as np
import RPi.GPIO as GPIO
from Time import Time
from sys import argv
import mpu9250

print(argv)

def main():
    #key init
    speed = 50
    HALF=0
    MOTOR_SPEEDS = {
        "q": (HALF, 1), "w": (1, 1), "e": (1, HALF),
        "a": (-1, 1), "s": (0, 0), "d": (1, -1),
        "z": (-HALF, -1), "x": (-1, -1), "c": (-1, -HALF),
    }

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
        
    #MPU init

    # Set up class
    gyro = 250      # 250, 500, 1000, 2000 [deg/s]
    acc = 2         # 2, 4, 7, 16 [g]
    tau = 0.98
    mpu = mpu9250.MPU(gyro, acc, tau)
    # Set up sensor and calibrate gyro with N points
    mpu.setUp()
    mpu.calibrateGyro(500)


    #PID init
    targetDeg = 0
    Kp = 3.
    Kd = 0.
    Ki = 10.
    dt = 0.5
    dt_sleep = 0.01
    tolerance = 0.01

    start_time = time.time()
    error_prev = 0.
    time_prev = 0.


    #socket 
    while True:
        conn = HTTPConnection(f"{argv[1] if len(argv) > 1 else  'localhost'}:{PORT}")

        try:
            conn.request("GET", "/")
        except ConnectionRefusedError as error:
            print(error)
            sleep(1)
            continue

        print('Connected')
             
#Control start
        action = "w"
        while True:                        


            #motor control
        
            if action in MOTOR_SPEEDS.keys():
                motorDeg = mpu.compFilter()

                pw1 = speed * MOTOR_SPEEDS[action][0]
                pw2 = speed * MOTOR_SPEEDS[action][1]

                #direction                                    
                if pw1>0:
                    GPIO.output(motor11,GPIO.HIGH)
                    GPIO.output(motor12,GPIO.LOW)
                elif pw1<0:
                    GPIO.output(motor11,GPIO.LOW)
                    GPIO.output(motor12,GPIO.HIGH)
                if pw2>0:
                    GPIO.output(motor21,GPIO.HIGH)
                    GPIO.output(motor22,GPIO.LOW)
                elif pw2<0:
                    GPIO.output(motor21,GPIO.LOW)
                    GPIO.output(motor22,GPIO.HIGH)  


                
                #PID start
                if action == "w":
                
                    error = targetDeg - motorDeg
                    de = error-error_prev
                    dt = time.time() - time_prev
                    control = Kp*error + Kd*de/dt + Ki*error*dt
                    error_prev = error
                    time_prev = time.time()

                    pw1_PID = max(min((abs(pw1) - control),100),0)  

                    #PID control   
                    if abs(error) >= tolerance:                 
                        p1.ChangeDutyCycle(pw1_PID)
                        p2.ChangeDutyCycle(abs(pw2))
                        print(pw1_PID, abs(pw2))
                    time.sleep(dt_sleep) 

                #General Control 
                else:                 
                    p1.ChangeDutyCycle(abs(pw1))
                    p2.ChangeDutyCycle(abs(pw2))
                    print(abs(pw1), abs(pw2))

                print("motorDeg :", motorDeg)
                
                    
main()
