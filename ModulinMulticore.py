#!/usr/bin/env python
import multiprocessing
from pyo import *
import math

import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115()

import Adafruit_MCP3008
import RPi.GPIO as GPIO
CLK  = 27
MISO = 22
MOSI = 17
CS1  = 8
CS2  = 9
mcp1 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS1, miso=MISO, mosi=MOSI)
mcp2 = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS2, miso=MISO, mosi=MOSI)

MAXADC = 26300.0

GPIO.setup(CS1,GPIO.OUT)
GPIO.setup(CS2,GPIO.OUT)

pa_list_devices()
#print pm_get_default_input()

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

notesFM = [87.31,
           98,
           103.83,
           116.54,
           130.81,
           138.59,
           155.56,
           174.61,
           196,
           207.65,
           233.08,
           261.63,
           277.18,
           311.13,
           349.23,
           392,
           415.3,
           466.16,
           523.25,
           554.37,
           622.25,
           698.46]

inputs = [
    '/m_prt',
    '/m_vibIn2',
    '/m_vibSep',
    '/m_pcSep',
    '/m_cutoff',
    '/m_res',
    '/m_distortion',
    '/m_volAffect',
    '/m_chanPan',
    '/m_dValue',
    '/m_dFeedB',
    '/m_attack',
    '/m_decay',
    '/m_sustain',
    '/m_release',
    '/m_wavetypenum',
    '/m_note',
    '/m_mod',
    '/m_vibIn',
    '/m_volIn',
    '/m_adsr',
    ]

class Proc(multiprocessing.Process):
    def __init__(self, create):
        super(Proc, self).__init__()
        self.daemon = True
        self.create = create

    def ribbon_sense(self):

        self.ribbon = adc.read_adc(0, gain=1)
        self.dis.value = notesFM[int((self.ribbon/MAXADC)*len(notesFM))]  # 25200

        self.vibratoribbon = adc.read_adc(1, gain=1)
        if self.vibratoribbon < 20000.0:
            self.vibIn.value = 0.0
        else:
            self.vibIn.value = (self.vibratoribbon - 20000.0) / 1000.0
        
        if self.vibratoribbon > 18000:
            self.adsr.value = 1.0
        else:
            self.adsr.value = 0.0

        self.wheel1 = adc.read_adc(2, gain=1)
        self.volIn.value = self.wheel1/MAXADC * 2.0 - 0.5

        self.wheel2 = adc.read_adc(3, gain=1)
        if self.wheel2 < 13380.0:
            self.mod.value = 1.0
        else:
            self.mod.value = 1.0 - ((self.wheel2-13380.0)/8720.0)

        #GPIO.output(CS2,1)
        #GPIO.output(CS1,0)

        #self.prt.value = mcp1.read_adc(4)/1024.0
        self.vibIn2.value = mcp1.read_adc(1)/1024.0
        self.vibSep.value = mcp1.read_adc(2)/1024.0
        self.ptSep.value = mcp1.read_adc(3)/1024.0
        self.dFeedB.value = mcp1.read_adc(0)/102.4
        self.dValue.value = mcp1.read_adc(4)/102.4
        self.chanPan.value = mcp1.read_adc(6)/1024.0
        self.distortion.value = mcp1.read_adc(7)/1024.0
        
        #GPIO.output(CS1,1)
        #GPIO.output(CS2,0)
        
        self.cutoff.value = mcp2.read_adc(0)/1024.0
        self.res.value = mcp2.read_adc(1)/1024.0
        self.volAffect.value = mcp2.read_adc(2)/1024.0
        self.attack.value = mcp2.read_adc(3)/1024.0
        self.decay.value = mcp2.read_adc(4)/1024.0
        self.sustain.value = mcp2.read_adc(5)/1024.0
        self.release.value = mcp2.read_adc(6)/1024.0
        self.prt.value = mcp2.read_adc(7)/1024.0
        
    def multifunctions(self):
        self.type2L.mul = self.waveTypeNum
        self.type1L.mul = 0.0
        self.type3L.mul = 0.0
        self.type4L.mul = 0.0
        self.type2R.mul = self.waveTypeNum
        self.type1R.mul = 0.0
        self.type3R.mul = 0.0
        self.type4R.mul = 0.0


    def run(self):
        # --Server setup--
        self.server = Server(audio='jack')  
        self.server.deactivateMidi()
        #self.server.setMidiInputDevice(3)
        #print pm_get_default_input()
        #print s.getMidiActive()
        self.server.setBufferSize(32)
        self.server.setDuplex(0)
        self.server.setOutputDevice(0)
        self.server.setNchnls(2)
        if self.create:
            self.server.setSamplingRate(16000)
        else:
            self.server.setSamplingRate(32000)
        self.server.boot()
        #print s.getMidiActive()
        print('Server booted!')
        self.server.amp = 0.25
        bufsize = self.server.getBufferSize()

        if self.create: # input handling
            self.dis = SigTo(440.0, time=0.1)
            self.mod = SigTo(0.5)
            self.prt = SigTo(0.5)
            self.vibIn = SigTo(0.0)
            self.vibIn2 = SigTo(0.2)
            self.vibSep = SigTo(0.5)
            self.ptSep = SigTo(0.0)
            self.volIn = SigTo(0.8)
            self.cutoff = SigTo(1.0)
            self.res = SigTo(0.0)
            self.distortion = SigTo(0.0)
            self.volAffect = SigTo(0.0)
            self.chanPan = SigTo(0.5)
            self.dValue = SigTo(0.0)
            self.dFeedB = SigTo(2.0)
            self.attack = SigTo(0.01)
            self.decay = SigTo(0.5)
            self.sustain = SigTo(0.7)
            self.release = SigTo(0.25)
            self.waveTypeNum = SigTo(1)
            self.adsr = Sig(0.0)
            #wtSlMap = SLMap(1, 4, 'lin', 'value', 1, 'int')
            #waveTypeNum.ctrl([wtSlMap], "Wave Type")

            self.inputlist = [
                self.dis, 
                self.mod, 
                self.prt, 
                self.vibIn, 
                self.vibIn2, 
                self.vibSep, 
                self.ptSep, 
                self.volIn, 
                self.cutoff, 
                self.res, 
                self.distortion, 
                self.volAffect, 
                self.chanPan,
                self.dValue,
                self.dFeedB,
                self.attack,
                self.decay,
                self.sustain,
                self.release,
                self.waveTypeNum,
                self.adsr,
                ]
                
            self.table = SharedTable(inputs, create=True, size=bufsize)
            self.recrd = TableFill(self.inputlist, self.table)

            ribP = Pattern(self.ribbon_sense, 0.1).play()
            
        else: # synth
            self.dis = TableScan(SharedTable(inputs[0], create=False, size=bufsize))
            self.mod = TableScan(SharedTable(inputs[1], create=False, size=bufsize))
            prt = TableScan(SharedTable(inputs[2], create=False, size=bufsize))
            self.vibIn = TableScan(SharedTable(inputs[3], create=False, size=bufsize))
            vibIn2 = TableScan(SharedTable(inputs[4], create=False, size=bufsize))
            vibSep = TableScan(SharedTable(inputs[5], create=False, size=bufsize))
            ptSep = TableScan(SharedTable(inputs[6], create=False, size=bufsize))
            self.volIn = TableScan(SharedTable(inputs[7], create=False, size=bufsize))
            cutoff = TableScan(SharedTable(inputs[8], create=False, size=bufsize))
            res = TableScan(SharedTable(inputs[9], create=False, size=bufsize))
            distortion = TableScan(SharedTable(inputs[10], create=False, size=bufsize))
            volAffect = TableScan(SharedTable(inputs[11], create=False, size=bufsize))
            chanPan = TableScan(SharedTable(inputs[12], create=False, size=bufsize))
            dValue = TableScan(SharedTable(inputs[13], create=False, size=bufsize))
            dFeedB = TableScan(SharedTable(inputs[14], create=False, size=bufsize))
            attack = TableScan(SharedTable(inputs[15], create=False, size=bufsize))
            decay = TableScan(SharedTable(inputs[16], create=False, size=bufsize))
            sustain = TableScan(SharedTable(inputs[17], create=False, size=bufsize))
            release = TableScan(SharedTable(inputs[18], create=False, size=bufsize))
            self.waveTypeNum = TableScan(SharedTable(inputs[19], create=False, size=bufsize))
            self.adsr = TableScan(SharedTable(inputs[20], create=False, size=bufsize))
   
            # --Startup noise--
            sn = Pan(Sine(440)).out()
            Clean_objects(1, sn).start()
            functions = Pattern(self.multifunctions, 0.1).play()
            
            # --Entire synth--
            porta = SigTo(value=self.dis, time=prt/5)
            pitch = porta - (self.mod-0.5)*100
            trVibL = self.vibIn*Sine((5-vibSep)*(vibIn2*5))*5
            trVibR = self.vibIn*Sine((5+vibSep)*(vibIn2*5))*5
            waveL = pitch + trVibL + (ptSep*5)
            waveR = pitch + trVibR - (ptSep*5)
            tri = TriTable()
            saw = SawTable()
            squ = SquareTable()
            self.type1L = Sine(waveL)
            self.type2L = Osc(saw, waveL)
            self.type3L = Osc(squ, waveL)
            self.type4L = Osc(tri, waveL)
            self.type1R = Sine(waveR)
            self.type2R = Osc(saw, waveR)
            self.type3R = Osc(squ, waveR)
            self.type4R = Osc(tri, waveR)
            audio1L = self.type1L + self.type2L + self.type3L + self.type4L
            audio1R = self.type1R + self.type2R + self.type3R + self.type4R
            
            #waveP = Pattern(self.wave_type, 0.5).play()
            self.type1L.mul = 0.0
            self.type2L.mul = 1.0
            self.type3L.mul = 0.0
            self.type4L.mul = 0.0
            self.type1R.mul = 0.0
            self.type2R.mul = 1.0
            self.type3R.mul = 0.0
            self.type4R.mul = 0.0
            
            fv = (Abs(self.vibIn) + self.volIn)*cutoff*1000
            LPF_L = MoogLP(audio1L, fv, res*2.0)
            LPF_R = MoogLP(audio1R, fv, res*2.0)
            srcL = Disto(LPF_L, distortion)
            srcR = Disto(LPF_R, distortion)
            self.env = MidiAdsr(self.adsr)#, attack=1.0)
            #env.ctrl()
            srcL.mul = (self.volIn+(trVibL*volAffect))
            srcR.mul = (self.volIn+(trVibR*volAffect))
            #mm = Mixer()
            #mm.addInput(0, srcL)
            #mm.addInput(1, srcR)
            #mm.setAmp(0, 0, 0.5)
            #mm.setAmp(1, 1, 0.5)
            LP = Pan(srcL, pan=chanPan).out()
            RP = Pan(srcR, pan=(1.0-chanPan)).out()
            LP.mul *= self.env
            RP.mul *= self.env
            srcDL = Delay(LP, dValue, dFeedB).out()
            srcDR = Delay(RP, dValue, dFeedB).out()
            #scope = Scope(LP+RP)
            # --End of synth--
            
        self.server.start()
        self.server.gui(locals())
            
if __name__ == '__main__':
    analysis = Proc(create=True)
    synthesis = Proc(create=False)
    print('Devices loaded')
    print('Starting servers...')
    analysis.start()
    synthesis.start()
