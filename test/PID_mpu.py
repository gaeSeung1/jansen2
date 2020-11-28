import RPi.GPIO as GPIO
import time

motor11=23
motor12=24
motor21=27
motor22=17
pwm1=25
pwm2=22


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(encPinA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(encPinB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pwmPin,GPIO.OUT)
GPIO.setup(dirPin,GPIO.OUT)

p = GPIO.PWM(19,100)
p.start(0)



encoderPos = 0

def encoderA(channel):
    global encoderPos
    if GPIO.input(encPinA) == GPIO.input(encPinB):
        encoderPos += 1
    else:
        encoderPos -= 1
   
def encoderB(channel):
    global encoderPos
    if GPIO.input(encPinA) == GPIO.input(encPinB):
        encoderPos -= 1
    else:
        encoderPos += 1



targetDeg= 0
#ratio = 360./270./64.
Kp = 1000.
Kd = 0.
Ki = 0.
dt = 0.
dt_sleep = 0.01
tolerance = 0.01

start_time = time.time()
error_prev = 0.
time_prev = 0.

while True:
    motorDeg = mpu.compFilter()
    error = targetDeg - motorDeg
    de = error-error_prev
    dt = time.time() - time_prev
    control = Kp*error + Kd*de/dt + Ki*error*dt;
    error_prev = error
    time_prev = time.time()
   
    GPIO.output(dirPin, control >= 0)
    p.ChangeDutyCycle(min(abs(control), 100))
    
    print('P-term = %7.1f, D-term = %7.1f, I-term = %7.1f' %(Kp*error, Kd*de/dt, Ki*de*dt))
    print('time = %6.3f, enc = %d, deg = %5.1f, err = %5.1f, ctrl = %7.1f' %(time.time()-start_time, encoderPos, motorDeg, error, control))
    print('%f, %f' %(de, dt))
 
    if abs(error) <= tolerance:
        GPIO.output(dirPin, control >= 0)
        p.ChangeDutyCycle(0)
        break
   
    time.sleep(dt_sleep)