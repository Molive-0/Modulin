#!/usr/bin/env python
from pyo import *
import math, time
import Adafruit_ADS1x15

RESIST = 1000000

adc = Adafruit_ADS1x15.ADS1115()

#--Server setup
#pa_list_devices()
s = Server()
s.setBufferSize(1024)
s.setDuplex(0)
s.setOutputDevice(3)
s.setNchnls(1)
s.setSamplingRate(32000)
s.boot()
print 'Server booted!'
s.amp = 0.5

notes = [65.41,
73.42,
82.41,
87.31,
98,
110,
123.47,
130.81,
146.83,
164.81,
174.61,
196,
220,
246.94,
261.63,
293.66,
329.63,
349.23,
392,
440,
493.88,
523.25,
587.33,
659.25,
698.46,
783.99,
880,
987.77,
1046.5]

ribbon = 0
smooth = 0.3
ribbon_s = SigTo(ribbon, time=0.25)
saw = SawTable()
se = Osc(saw,ribbon_s)
#se2 = Osc(saw,ribbon_s+5)
def ribbonsense():
    global ribbon
    ribbon = adc.read_adc(1)#(smooth*ribbon)+((1-smooth)*adc.read_adc(1))
    #if (ribbon < 4000) and se.mul == 0.0:
    #    ribbon = adc.read_adc(1)
    #print ribbon
    #ribbon = (ribbon*RESIST)/(65535.01-ribbon)
    #ribbon = round(ribbon/10000)*100
    ribbon_s.value = notes[int(ribbon/1000)]
    #ribbon_s.mul = 0.01
    if ribbon > 4000:
        #se.mul = 0.0
        pass
    else:
        se.mul = 1.0
    #print ribbon
    #print se.mul
    #print ribbon/100
p = Pattern(ribbonsense, 0.1).play()
se.out()
#se2.out()

s.start()
s.gui(locals())
