#!/usr/bin/env python
from pyo import *
import math, time

pa_list_devices()
pm_list_devices()
#print pm_get_default_input()

#--Server setup
s = Server()
s.setMidiInputDevice(1)
#print pm_get_default_input()
#print s.getMidiActive()
s.setBufferSize(1024)
s.setDuplex(0)
s.setOutputDevice(0)
s.setNchnls(1)
s.setSamplingRate(32000)
s.boot()
#print s.getMidiActive()
print 'Server booted!'
#s.amp = 0.5

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
sn = Sine(440).out()
def call():
    sn.stop()
cafter = CallAfter(call, 1)
    
#--Entire synth
note = Notein(scale=1,poly=10)
#note = Choice([440,220,880],4)
#dis=note
dis=note['pitch']
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
#vibin.setValue(0.5)
volin = Sig(0.5)
volin.ctrl(title='Volume')
trvib = vibin*Sine(5)*5
wave = pitch + trvib
#out = Sine(wave).out()
tri = TriTable()
saw = SawTable()
squ = SquareTable()
wavetypenum = Sig(1)
wtslmap = SLMap(1,4,'lin','value',1,'int')
wavetypenum.ctrl([wtslmap],"Wave Type")
type1 = Sine(wave)
type2 = Osc(saw,wave)
type3 = Osc(squ,wave)
type4 = Osc(tri,wave)
audio1 = type1 + type2 + type3 + type4
def wavetype():
    if wavetypenum.value.value == 1:
        type1.mul = 1.0
        type2.mul = 0.0
        type3.mul = 0.0
        type4.mul = 0.0
    elif wavetypenum.value.value == 2:
        type1.mul = 0.0
        type2.mul = 1.0
        type3.mul = 0.0
        type4.mul = 0.0
    elif wavetypenum.value.value == 3:
        type1.mul = 0.0
        type2.mul = 0.0
        type3.mul = 1.0
        type4.mul = 0.0
    elif wavetypenum.value.value == 4:
        type1.mul = 0.0
        type2.mul = 0.0
        type3.mul = 0.0
        type4.mul = 1.0
    else:
        type1.mul = 1.0
        type2.mul = 0.0
        type3.mul = 0.0
        type4.mul = 0.0
p = Pattern(wavetype, 0.4).play()
def pstart():
    p.play()
#CallAfter(pstart,1)
#audio1.out()
sabs = Abs(vibin)
fv = sabs + volin
cutoff = Sig(1.0)
cutoff.ctrl(title='LPF Cutoff')
fv5 = fv*cutoff*1000
LPF = Tone(audio1,fv5)
#LPF.ctrl()
src = LPF
#env = MidiAdsr(note['velocity'],attack=0.01,decay=0.5,sustain=0.7,release=0.25)
#env.ctrl()
#env.play()
src.mul = volin*2
src.out()
#-- End of synth

print 'Devices loaded'
print 'Starting server...'
#scope = Scope(src)
s.start()
s.gui(locals())
