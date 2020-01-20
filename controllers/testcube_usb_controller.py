import usb.core
from usb.backend import libusb1
import usb.util
import time


class PwmMessage:
    def __init__(self):
        self.Freq = [None] * 2
        self.Hiconf = [None] * 12

        self.PwmEnabled = [None] * 12
        self.Duty = [None] * 12
        
    def setPwmFrequency(self, bank: int, hz: int):
        self.Freq[bank] = hz

    def sethiconf(self, idx: int, activehi: bool):
        self.Hiconf[idx] = activehi

    def setPwmDutyCycle(self, idx: int, duty: int):
        self.Duty[idx] = duty

    def setPwmEnabled(self, idx: int, enabled: bool):
        self.PwmEnabled[idx] = enabled

    def getUsbMsg8(self):
        if self.PwmEnabled == [None] * 12:
            return []
        mask = 0
        val = 0
        for i in range(0,len(self.PwmEnabled)): 
            if self.PwmEnabled[i] != None:
                mask |= (1<<i)
                if self.PwmEnabled[i]:
                    val |= (1<<i)           
        r = "{:08x}{:04x}{:04x}".format(
            0x08,mask,val)
        return [r]

    def getUsbMsg6(self,bank:int):
        if self.Duty[bank*6:bank*6+6] == ([None] * 6):
            return []
        
        dutymask = 0
        for i in range(6):
            if self.Duty[i+bank*6] != None:
                dutymask |= (1<<i)
        r = "{:08x}{:02x}{:02x}".format(
            0x06,bank,dutymask) 
        for i in range(6): 
            r += "{:02x}".format(self.Duty[i+bank*6] or 0) 
        return [r]           
                    

    def getUsbMsg4(self):
        if (self.Freq == [None]*2) and (self.Hiconf == [None]*12):
            return []
        freqmask=0x0
        hilomask=0x000
        hiloval=0x000
        for i in range(0,len(self.Freq)): 
            if self.Freq[i] != None:
                freqmask |= (8>>i)

        for i in range(0,len(self.Hiconf)): 
            if self.Hiconf[i] != None:
                hilomask |= (1<<i)
                if self.Hiconf[i]:
                    hiloval |= (1<<i)

        try:
            assert(freqmask<=0xf)
            assert(hilomask<=0xfff)
            assert(hiloval<=0xfff)
        except:
            raise ValueError('PwmMessageFieldOverflow')

        r = "{:08x}{:01x}{:03x}0{:03x}{:04x}{:04x}".format(
            0x04,freqmask,hilomask,hiloval,self.Freq[0] or 0,self.Freq[1] or 0)
        return [r]


    def get_pwm_messages(self):
        return (self.getUsbMsg4() +
         self.getUsbMsg6(0) + 
         self.getUsbMsg6(1) + 
         self.getUsbMsg8())

class RelayMessage:
    def __init__(self):
        self.RelayStates = [None,None,None,None,None,None]        
        
    def setRelay(self, relay, state):
        self.RelayStates[relay] = state

    def get_relay_messages(self):
        if self.RelayStates == [None] * 6:
            return []
        mask = 0
        val = 0
        for i in range(0,len(self.RelayStates)): 
            if self.RelayStates[i] != None:
                mask |= (1<<i)
                if self.RelayStates[i]:
                    val |= (1<<i)   
        r = "{:08x}{:02x}{:02x}".format(
               0x12,mask,val)
        return [r]

class DiMessage:
    def __init__(self):
        self.dimonitorrate = None 

    def setDiMonitorUpdateRate(self,rate:int):
        self.dimonitorrate = rate

    def get_di_messages(self):
        if self.dimonitorrate == None:
            return []
        r = "{:08x}{:02}".format(
            0xa,self.dimonitorrate
        ) 
        return [r]

class ActCurMessage:
    def __init__(self):
        self.actmonitorRate = None 
        self.actmonitorChannels = None
        self.actmonitorThreshold = None

    def setPwmCurrentMonitorUpdateRate(self,rate:int):
        self.actmonitorRate = rate
    
    def setPwmFaultThreshold(self,Threshold:int):
        self.actmonitorThreshold = Threshold

#    def setPwmFaultDelay(self):

    def setPwmCurrentMonitorChannels(self,channelMask:int):
        self.actmonitorChannels = channelMask

    def get_actcur_messages(self):
        if self.actmonitorChannels == None:
            return []
        if self.actmonitorRate == None:
            return []
        if self.actmonitorThreshold == None:
            return []

        r = "{:08x}{:04x}{:02x}{:02x}".format(
            0xc,self.actmonitorChannels,self.actmonitorRate,self.actmonitorThreshold
        ) 
        return [r]            

class FrequencyMessage:
    def __init__(self):
        self.freqmonitorRate = None 
        self.freqmonitorChannels = None

    def setFrequencyInputEnabled(self,freqmask:int):
        self.freqmonitorChannels = freqmask
        
    def setFrequencyMonitorRate(self,rate):
        self.freqmonitorRate = rate

    def get_freq_messages(self):
        if self.freqmonitorRate == None:
            return []
        if self.freqmonitorChannels == None:
            return []   

        r = "{:08x}{:02x}{:02x}".format(
            0xe,self.freqmonitorChannels,self.freqmonitorRate
        ) 
        return [r]          

class UsbMessage:
    def __init__(self):
        self.usbmsg = None
    def sendrawusb(self,msg):
        self.usbmsg = msg
    def get_sendusb_messages(self):    
        if self.usbmsg == None:
            return []
        return [self.usbmsg]

class TestCubeUSB(
    RelayMessage,
    PwmMessage,
    DiMessage,
    ActCurMessage,
    UsbMessage,
    FrequencyMessage
    ):
    
    def callParentInits(self):
        RelayMessage.__init__(self)
        PwmMessage.__init__(self)
        DiMessage.__init__(self)
        ActCurMessage.__init__(self)
        UsbMessage.__init__(self)
        FrequencyMessage.__init__(self)

    def __init__(self):
        callParentInits()

    def start(self):
        self.dev = usb.core.find(idVendor=0x2B87,idProduct=0x0001)
        if self.dev is None:
            raise ValueError('Device not found')
        self.dev.set_configuration()

    def finish(self):
        msgs = (self.get_relay_messages()
            + self.get_pwm_messages()
            + self.get_di_messages()
            + self.get_actcur_messages()
            + self.get_sendusb_messages()
            + self.get_freq_messages()
        )
        for msg in msgs:
            self.dev.write(2, msg)
        callParentInits()

