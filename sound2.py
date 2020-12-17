import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(15, GPIO.IN)

n = 0
while True:
    if GPIO.input(15):
        #print('Noisy', n)
        n += 1
    else:
        #print('Quiet')
        n = 0
    
    if n == 4:
        print('Sound', n)
        n = 0
    time.sleep(0.01)