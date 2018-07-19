import RPi.GPIO as GPIO
import time
from math import sin

GPIO.setmode(GPIO.BCM)
GPIO.setup(9, GPIO.OUT)
i = 0
while True:
    GPIO.output(9,1)
    time.sleep((sin(i)+1)/4.0)
    GPIO.output(9,0)
    time.sleep((sin(i)+1)/4.0)
    i+=1
