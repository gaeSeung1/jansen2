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

# motor action init
speed = 50
HALF=0
MOTOR_SPEEDS = {
    ord("q"): (HALF, 1), ord("w"): (1, 1), ord("e"): (1, HALF),
    ord("a"): (-1, 1), ord("s"): (0, 0), ord("d"): (1, -1),
    ord("z"): (-HALF, -1), ord("x"): (-1, -1), ord("c"): (-1, -HALF),
}


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
    elif action == ord('x'):
        print('back')


sound = 10
GPIO.setup(sound, GPIO.IN)

n = 0

while True:
    if GPIO.input(sound):
        pass
        n = 0

    #sound detect
    else:
        n += 1

    if n == 2:
        motor(ord('x'))
        time.sleep(1)
        motor(ord('s'))
        n = 0



    time.sleep(0.01)
        


