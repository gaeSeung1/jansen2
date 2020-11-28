PORT = 6000

from http.client import HTTPConnection
import json
from time import sleep
import numpy as np
import RPi.GPIO as GPIO
from Time import Time
from sys import argv

print(argv)

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
     

def main():
 
    #initialization
    speed = 50
    HALF=0
    MOTOR_SPEEDS = {
        "q": (HALF, 1), "w": (1, 1), "e": (1, HALF),
        "a": (-1, 1), "s": (0, 0), "d": (1, -1),
        "z": (-HALF, -1), "x": (-1, -1), "c": (-1, -HALF),
    }

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
        res = conn.getresponse()
        
        
        while True:                        
            
            chunk = res.readline()
            if (chunk == b'\n'): continue
            if (not chunk): break

            chunk = chunk[:-1].decode()
            data = json.loads(chunk)
            print(Time(), data)
            action = data['action']

#Control start

            #speed 50 or 100
            if action == "\t":

                if speed == 100:
                    speed = 50
                else:
                    speed = 100
                print("speed :",speed)

            else:
                None

            #motor control
            if action in MOTOR_SPEEDS.keys():
                pw1 = speed * MOTOR_SPEEDS[action][0]
                pw2 = speed * MOTOR_SPEEDS[action][1]

                try:    
                                    
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

                    p1.ChangeDutyCycle(abs(pw1))
                    p2.ChangeDutyCycle(abs(pw2))
                    

                except KeyError as error:
                    print(error)


main()
