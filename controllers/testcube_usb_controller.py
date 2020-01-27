import usb.core
from usb.backend import libusb1
import usb.util
import time, threading, time
from pubsub import pub


class AdcMessage:
    def __init__(self):
        self.AdcChannels = None
        self.AdcRate = None
    
    def setAdcMonitorUpdateRate(self,rate:int):
        self.AdcRate = rate

    def setAdcEnabled(self,mask:int):
        self.AdcChannels = mask

    def get_adc_messages(self):
        if self.AdcChannels == None:
            return []
        if self.AdcRate == None:
            return []
        r = "{:08x}{:02x}{:02x}".format(
            0x10,self.AdcChannels,self.AdcRate
        ) 
        return [r]


class PwmMessage:
    def __init__(self):
        self.Freq = [None] * 2
        self.Hiconf = [None] * 12

        self.PwmEnabled = [None] * 12
        self.Duty = [None] * 12
        
    def setPwmFrequencyA(self, hz: int):
        self.Freq[0] = hz

    def setPwmFrequencyB(self, hz: int):
        self.Freq[1] = hz

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
        
    def setRelay(self, relay: int, state: bool):
        print(f"state: {state} type: {type(state)}")
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
        r = "{:08x}{:02x}".format(
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
    FrequencyMessage,
    AdcMessage
    ):
    
    def callParentInits(self):
        RelayMessage.__init__(self)
        PwmMessage.__init__(self)
        DiMessage.__init__(self)
        ActCurMessage.__init__(self)
        UsbMessage.__init__(self)
        FrequencyMessage.__init__(self)
        AdcMessage.__init__(self)

    def __init__(self):
        self.callParentInits()
        self.usbidparsers = {
            '00000005':self.recusb_5_pwmfreq,
            '00000007':self.recusb_7_pwmdutycycle,
            '00000009':self.recusb_9_pwmenable,
            '0000000b':self.recusb_b_digitalinputs,
            '0000000d':self.recusb_00d_actcurrent,
            '0000010d':self.recusb_10d_actcurrent,
            '0000020d':self.recusb_20d_actcurrent,
            '0000030d':self.recusb_30d_actcurrent,
            '0000000f':self.recusb_00f_speed,
            '0000010f':self.recusb_10f_speed,
            '00000011':self.recusb_011_adc,
            '00000111':self.recusb_111_adc,
            '00000211':self.recusb_211_adc,
            '00000013':self.recusb_13_relay,
            '0000001d':self.recusb_1d_actfault,
            '00000041':self.recusb_41_version,
            }

    def start(self):
        self.dev = usb.core.find(idVendor=0x2B87,idProduct=0x0001)
        print(f"start: {self.dev}")
        if self.dev is None:
            raise ValueError('Device not found')
        self.dev.set_configuration()

    def finished(self):
        print(f"finished: {self.dev}")
        msgs = (self.get_relay_messages()
            + self.get_pwm_messages()
            + self.get_di_messages()
            + self.get_actcur_messages()
            + self.get_sendusb_messages()
            + self.get_freq_messages()
            + self.get_adc_messages()
        )
        for msg in msgs:
            print(msg)
            self.dev.write(2, msg)
        callParentInits()

    def usbrxhandler(self):
        msg = pollusb()
        d = recUsb(msg)
        sendthistochris(d)

    def recUsb(self,msg):
        id, payload = msg[:8], msg[8:]
        f = self.usbidparsers.get(id)
        if f is None:
            raise ("invalid id")
            return []
        return f(payload)

      
    def recusb_5_pwmfreq(self,payload):
        acthi,freqa,freqb = payload[:4],payload[4:8],payload[8:12]
        #print(acthi,freqa,freqb)
        d = []
        path = '/pwmController/bankA/frequency'
        data = int(freqa,16)
        d.append({'path':path,'data':data})
        path = '/pwmController/bankB/frequency'
        data = int(freqb,16)
        d.append({'path':path,'data':data})
        path = '/pwmController/pwms'
        data = [{'activeConfiguration':"high"} if (int(acthi,16) & (1<<x)) else {'activeConfiguration':"low"} for x in range(12)]
        d.append({'path':path,'data':data})
        return d
    def recusb_7_pwmdutycycle(self,payload):
        raise("not implemented")
    def recusb_9_pwmenable(self,payload):
        raise("not implemented")
    def recusb_b_digitalinputs(self,payload):
        raise("not implemented")
    def recusb_00d_actcurrent(self,payload):
        raise("not implemented")
    def recusb_10d_actcurrent(self,payload):
        raise("not implemented")
    def recusb_20d_actcurrent(self,payload):
        raise("not implemented")
    def recusb_30d_actcurrent(self,payload):
        raise("not implemented")
    def recusb_00f_speed(self,payload):
        raise("not implemented")
    def recusb_10f_speed(self,payload):
        raise("not implemented")
    def recusb_011_adc(self,payload):
        raise("not implemented")
    def recusb_111_adc(self,payload):
        raise("not implemented")
    def recusb_211_adc(self,payload):
        raise("not implemented")
    def recusb_13_relay(self,payload):
        raise("not implemented")
    def recusb_1d_actfault(self,payload):
        raise("not implemented")
    def recusb_41_version(self,payload):
        raise("not implemented")
