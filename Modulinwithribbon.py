#!/usr/bin/env python
from pyo import *
RIBBON_MODE = 1

if RIBBON_MODE == 1:
    import Adafruit_ADS1x15
    adc = Adafruit_ADS1x15.ADS1115()

pa_list_devices()
pm_list_devices()
#print pm_get_default_input()

# --Server setup--
s = Server()
s.setMidiInputDevice(3)
#print pm_get_default_input()
#print s.getMidiActive()
s.setBufferSize(512)
s.setDuplex(0)
s.setOutputDevice(1)
s.setNchnls(2)
s.setSamplingRate(16000)
s.boot()
#print s.getMidiActive()
print('Server booted!')
s.amp = 0.25


# --TriTable import from examples-- (Not in normal libs?)
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
        for i in range(1, order*2):
            if i % 2 == 0:
                l.append(0)
            else:
                l.append(ph / (i*i))
                ph *= -1
        return l
    
    def set_order(self, x):
        self._order = x
        self._tri_table.replace(self._create_list(x))
        self.normalize()
        self.refreshView()

    @property
    def order(self): 
        return self._order

    @order.setter
    def order(self, x): self.set_order(x)


def call2():
    LP.out()
    RP.out()
    
    
def ribbon_sense():
    ribbon = adc.read_adc(0, gain=2/3)
    note.value = notes[int((ribbon/25250.0)*len(notes))]  # 25200

    #vibratoribbon = adc.read_adc(1, gain=2/3)
    #vibIn.value = vibratoribbon / 1000.0

    wheel1 = adc.read_adc(2, gain=2/3)
    volIn.value = wheel1 / 25250.0 * 1.5

    #wheel2 = adc.read_adc(3, gain=2/3)
    #mod.value = (wheel2 - 18000) / 1000.0
    
    
# --Startup noise--
sn = Pan(Sine(440)).out()
Clean_objects(1, sn).start()
cAfter2 = CallAfter(call2, 1.5)


# --Notes--
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

# --Ribbon handling--
if RIBBON_MODE == 1:
    note = SigTo(0.0, time=0.1)
    ribP = Pattern(ribbon_sense, 0.2).play()
    dis = note
else:
    note = Notein(scale=1, poly=1)
    dis = note["pitch"]
    
# --Entire synth--
mod = Sig(0.5)
#mod.ctrl(title='Modulation')
prt = Sig(0.5)
prt.ctrl(title="Portamento")
porta = SigTo(value=dis, time=prt/5)
pitch = porta - (mod-0.5)*100
vibIn = Sig(0.0)
#vibIn.ctrl(title='Vibrato Depth')
vibIn2 = Sig(0.2)
vibIn2.ctrl(title='Vibrato Frequency')
vibSep = Sig(0.5)
vibSep.ctrl(title='Vibrato Channel Separation')
ptSep = Sig(0.0)
ptSep.ctrl(title='Pitch Channel Separation')
volIn = Sig(0.5)
#volIn.ctrl(title='Volume')
trVibL = vibIn*Sine((5-vibSep)*(vibIn2*5))*5
trVibR = vibIn*Sine((5+vibSep)*(vibIn2*5))*5
waveL = pitch + trVibL + (ptSep*5)
waveR = pitch + trVibR - (ptSep*5)
tri = TriTable()
saw = SawTable()
squ = SquareTable()
waveTypeNum = Sig(1)
wtSlMap = SLMap(1, 4, 'lin', 'value', 1, 'int')
waveTypeNum.ctrl([wtSlMap], "Wave Type")
type1L = Sine(waveL)
type2L = Osc(saw, waveL)
type3L = Osc(squ, waveL)
type4L = Osc(tri, waveL)
type1R = Sine(waveR)
type2R = Osc(saw, waveR)
type3R = Osc(squ, waveR)
type4R = Osc(tri, waveR)
audio1L = type1L + type2L + type3L + type4L
audio1R = type1R + type2R + type3R + type4R


def wave_type():
    if waveTypeNum.value.value == 1:
        type1L.mul = 1.0
        type2L.mul = 0.0
        type3L.mul = 0.0
        type4L.mul = 0.0
        type1R.mul = 1.0
        type2R.mul = 0.0
        type3R.mul = 0.0
        type4R.mul = 0.0
    elif waveTypeNum.value.value == 2:
        type1L.mul = 0.0
        type2L.mul = 1.0
        type3L.mul = 0.0
        type4L.mul = 0.0
        type1R.mul = 0.0
        type2R.mul = 1.0
        type3R.mul = 0.0
        type4R.mul = 0.0
    elif waveTypeNum.value.value == 3:
        type1L.mul = 0.0
        type2L.mul = 0.0
        type3L.mul = 1.0
        type4L.mul = 0.0
        type1R.mul = 0.0
        type2R.mul = 0.0
        type3R.mul = 1.0
        type4R.mul = 0.0
    elif waveTypeNum.value.value == 4:
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

waveP = Pattern(wave_type, 1).play()

sAbs = Abs(vibIn)
fv = sAbs + volIn
cutoff = Sig(1.0)
cutoff.ctrl(title='LPF Cutoff')
res = Sig(0.0)
res.ctrl(title='LPF Resonance')
distortion = Sig(0.0)
distortion.ctrl(title='Distortion')
fv5 = fv*cutoff*1000
LPF_L = MoogLP(audio1L, fv5, res*2.0)
LPF_R = MoogLP(audio1R, fv5, res*2.0)
srcL = Disto(LPF_L, distortion)
srcR = Disto(LPF_R, distortion)
#env = MidiAdsr(note['velocity'], attack=0.01, decay=0.5, sustain=0.7, release=0.25)
#env.ctrl()
volAffect = Sig(0.0)
volAffect.ctrl(title='Affect Of Vibrato On Volume')
srcL.mul = (volIn+(trVibL*volAffect))
srcR.mul = (volIn+(trVibR*volAffect))
mm = Mixer()
mm.addInput(0, srcL)
mm.addInput(1, srcR)
mm.setAmp(0, 0, 0.5)
mm.setAmp(1, 1, 0.5)
chanPan = Sig(0.5)
chanPan.ctrl(title='Channel Panning')
LP = Pan(mm[0], pan=chanPan)
RP = Pan(mm[1], pan=(1.0-chanPan))
#LP.mul *= env
#RP.mul *= env
dValue = Sig(0.0)
dValue.ctrl(title='Delay Offset')
dFeedB = Sig(0.0)
dFeedB.ctrl(title='Delay Feedback')
srcDL = Delay(LP, dValue, dFeedB).out()
srcDR = Delay(RP, dValue, dFeedB).out()
# --End of synth--

print('Devices loaded')
print('Starting server...')
#scope = Scope(LP+RP)
s.start()
s.gui(locals())
