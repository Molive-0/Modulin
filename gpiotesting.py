import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(1, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(14, GPIO.OUT)
while True:
    GPIO.output(21,1)
    GPIO.output(20, 1)
    GPIO.output(16, 1)
    GPIO.output(12, 1)
    GPIO.output(1, 1)
    GPIO.output(7, 1)
    GPIO.output(8, 1)
    GPIO.output(25, 1)
    GPIO.output(21, 1)
    GPIO.output(23, 1)
    GPIO.output(10, 1)
    GPIO.output(15, 1)
    GPIO.output(14, 1)
    time.sleep(1)
    GPIO.output(21,0)
    GPIO.output(20, 0)
    GPIO.output(16, 0)
    GPIO.output(12, 0)
    GPIO.output(1, 0)
    GPIO.output(7, 0)
    GPIO.output(8, 0)
    GPIO.output(25, 0)
    GPIO.output(21, 0)
    GPIO.output(23, 0)
    GPIO.output(10, 0)
    GPIO.output(15, 0)
    GPIO.output(14, 0)
    time.sleep(1)
