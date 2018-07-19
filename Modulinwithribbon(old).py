#!/usr/bin/env python
from pyo import *
import math, time
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()

#pa_list_devices()
#pm_list_devices()
#print pm_get_default_input()

#--Server setup
s = Server()
s.setMidiInputDevice(3)
#print pm_get_default_input()
#print s.getMidiActive()
s.setBufferSize(1024)
s.setDuplex(0)
s.setOutputDevice(3)
s.setNchnls(2)
s.setSamplingRate(32000)
s.boot()
#print s.getMidiActive()
print 'Server booted!'
s.amp = 0.25

#--TriTable import from examples (Not in normal libs?)
class TriTable(PyoTableObject):
    def __init__(self, order=10, size=8192):
        PyoTableObject.__init__(self, size)
        self._order = order
        self._tri_table = HarmTable(self._create_list(order), size)
        self._base_objs = self._tri_table.getBaseObjects()
        self.normalize()

    def _create_list(self, order):
        l = []
        ph = 1.0
        for i in range(1,order*2):
            if i % 2 == 0:
                l.append(0)
            else:
                l.append(ph / (i*i))
                ph *= -1
        return l
    
    def setOrder(self, x):   
        self._order = x
        self._tri_table.replace(self._create_list(x))
        self.normalize()
        self.refreshView()

    @property
    def order(self): 
        return self._order
    @order.setter
    def order(self, x): self.setOrder(x)

#--Startup noise
sn = Pan(Sine(440)).out()
def call1():
    sn.stop()
def call2():
    LP.out()
    RP.out()
cafter1 = CallAfter(call1, 1)
cafter2 = CallAfter(call2, 1.5)

#--Notes
notes = [65.41,73.42,82.41,87.31,98,110,123.47,130.81,146.83,164.81,174.61,196,220,246.94,261.63,293.66,329.63,349.23,392,440,493.88,523.25,587.33,659.25,698.46,783.99,880,987.77,1046.5]

#--Ribbon handling
ribbon = 0
smooth = 0.3
note = SigTo(ribbon, time=0.1)

def ribbonsense():
    global ribbon
    ribbon = adc.read_adc(1,gain=2/3)
    #print ribbon
    #print (ribbon/25250.0)
    note.value = notes[int((ribbon/25250.0)*len(notes))] #25200
ribp = Pattern(ribbonsense, 0.1).play()

#--Entire synth
#note = Choice([440,220,880],4)
#dis=note
dis=note
mod = Sig(0.5)
mod.ctrl(title='Modulation')
#mod.setValue(0.5)
prt = Sig(0.5)
prt.ctrl(title="Portamento")
porta = SigTo(value=dis,time=prt/5)
mod5 = mod-0.5
trmod = mod5*100
pitch = porta - trmod
#out = Sine(freq=pitch)
vibin = Sig(0.0)
vibin.ctrl(title='Vibrato')
vibsep = Sig(0.5)
vibsep.ctrl(title='Vibrato Channel Seperation')
ptsep = Sig(0.0)
ptsep.ctrl(title='Vitch Channel Seperation')
#vibin.setValue(0.5)
volin = Sig(0.5)
volin.ctrl(title='Volume')
trvibL = vibin*Sine(5-vibsep)*5
trvibR = vibin*Sine(5+vibsep)*5
waveL = pitch + trvibL + (ptsep*5)
waveR = pitch + trvibR - (ptsep*5)
#out = Sine(wave).out()
tri = TriTable()
saw = SawTable()
squ = SquareTable()
wavetypenum = Sig(1)
wtslmap = SLMap(1,4,'lin','value',1,'int')
wavetypenum.ctrl([wtslmap],"Wave Type")
type1L = Sine(waveL)
type2L = Osc(saw,waveL)
type3L = Osc(squ,waveL)
type4L = Osc(tri,waveL)
type1R = Sine(waveR)
type2R = Osc(saw,waveR)
type3R = Osc(squ,waveR)
type4R = Osc(tri,waveR)
audio1L = type1L + type2L + type3L + type4L
audio1R = type1R + type2R + type3R + type4R
def wavetype():
    if wavetypenum.value.value == 1:
        type1L.mul = 1.0
        type2L.mul = 0.0
        type3L.mul = 0.0
        type4L.mul = 0.0
        type1R.mul = 1.0
        type2R.mul = 0.0
        type3R.mul = 0.0
        type4R.mul = 0.0
    elif wavetypenum.value.value == 2:
        type1L.mul = 0.0
        type2L.mul = 1.0
        type3L.mul = 0.0
        type4L.mul = 0.0
        type1R.mul = 0.0
        type2R.mul = 1.0
        type3R.mul = 0.0
        type4R.mul = 0.0
    elif wavetypenum.value.value == 3:
        type1L.mul = 0.0
        type2L.mul = 0.0
        type3L.mul = 1.0
        type4L.mul = 0.0
        type1R.mul = 0.0
        type2R.mul = 0.0
        type3R.mul = 1.0
        type4R.mul = 0.0
    elif wavetypenum.value.value == 4:
        type1L.mul = 0.0
        type2L.mul = 0.0
        type3L.mul = 0.0
        type4L.mul = 1.0
        type1R.mul = 0.0
        type2R.mul = 0.0
        type3R.mul = 0.0
        type4R.mul = 1.0
    else:
        type1L.mul = 1.0
        type2L.mul = 0.0
        type3L.mul = 0.0
        type4L.mul = 0.0
        type1R.mul = 1.0
        type2R.mul = 0.0
        type3R.mul = 0.0
        type4R.mul = 0.0
wavep = Pattern(wavetype, 1).play()
def pstart():
    p.play()
#CallAfter(pstart,1)
#audio1.out()
sabs = Abs(vibin)
fv = sabs + volin
cutoff = Sig(1.0)
cutoff.ctrl(title='LPF Cutoff')
fv5 = fv*cutoff*1000
LPF_L = Tone(audio1L,fv5)
LPF_R = Tone(audio1R,fv5)
#LPF.ctrl()
srcL = LPF_L
srcR = LPF_R
#env = MidiAdsr(note['velocity'],attack=0.01,decay=0.5,sustain=0.7,release=0.25)
#env.ctrl()
#env.play()
volaffect = Sig(0.0)
volaffect.ctrl(title='Affect Of Vibrato On Volume')
srcL.mul = volin+(trvibL*volaffect)
srcR.mul = volin+(trvibR*volaffect)
mm = Mixer()
mm.addInput(0,srcL)
mm.addInput(1,srcR)
mm.setAmp(0,0,0.5)
mm.setAmp(1,1,0.5)
chanpan = Sig(0.5)
chanpan.ctrl(title='Channel Panning')
glopan = Sig(0.5)
glopan.ctrl(title='Global Panning')
LP = Pan(mm[0],pan=(chanpan)*(1.0-glopan))
RP = Pan(mm[1],pan=(1.0-chanpan)*(1.0-glopan))
#-- End of synth

print 'Devices loaded'
print 'Starting server...'
#scope = Scope(src)
s.start()
s.gui(locals())
