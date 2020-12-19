import RPi.GPIO as GPIO
import time

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

balance = 1.1
#motor action init
MOTOR_SPEEDS = {
    "1": (0, 1), "2" : (1, 0), 
    "q": (-0.3, 1), "w": (1, 1), "e": (1, -0.3),
    "a": (-1, 1), "s": (0, 0), "d": (1, -1),
    "z": (0, -1), "x": (-1, -1), "c": (-1, 0),
}

def motor(action, speed):
    pw1 = min(speed * MOTOR_SPEEDS[action][0] * balance, 100)
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
    if action == 's':
        print('stop')
    elif action == 'a':
        print('left')
    elif action == 'd':
        print('right')
    elif action == 'x':
        print('back')
    elif action == 'w':
        print('forward')


sound = 10
GPIO.setup(sound, GPIO.IN)

detect = 0
detect_1st = 0
mode = 0
switch = 1

start = int(time.strftime('%S'))

while True:
    finish = int(time.strftime('%S'))
    if switch == 1:
        if GPIO.input(sound):
            pass

        #sound detect
        else:
            detect += 1
            time.sleep(0.2)

        print(detect_1st, detect, finish, start)
        #first detect
        if detect == 1 and detect_1st != 1:
            start = int(time.strftime('%S'))
            print('detect start')
            detect_1st = 1
        
        second = 2
        if finish - start == second or finish - start == second-60:
            if detect >= 1:
                mode = detect
                print('detect finish, mode :', mode)
                switch = 0
                
                if mode >= 1:
                    if mode == 1:
                        motor('w', 60)
                        time.sleep(1)
            
                    elif mode == 2:
                        motor('a', 70)
                        time.sleep(0.7)
            
                    elif mode == 3:
                        motor('d', 70)
                        time.sleep(0.7)
            
                    elif mode == 4:
                        motor('x', 70)
                        time.sleep(1)
            
                    elif mode >= 5:
                        motor('w', 60)
                        time.sleep(5)

                    motor('s', 0)

                    switch = 1
                    detect = 0
                    detect_1st = 0
                    time.sleep(0.5)

    time.sleep(0.01)
        


