import usb.core
from usb.backend import libusb1
import usb.util
import time, threading, time
from pubsub import pub


class AdcMessage:
    def __init__(self):
        self.AdcChannels = 0x3F
        self.AdcRate = None
    
    def setAdcMonitorUpdateRate(self,rate:int):
        print(f"testcubeUSB: setAdcMonitorUpdateRate")
        self.AdcRate = int(rate / 50)

    def setAdcEnabled(self,enabled:bool,channel:int):
        print(f"testcubeUSB: setAdcEnabled: {channel=}")
        if enabled: self.AdcChannels |= 1 << channel 
        else: self.AdcChannels &= ((1 << channel) ^ 0xff)

    def get_adc_messages(self):
        if self.AdcChannels == None:
            return []
        if self.AdcRate == None:
            return []
        return [f"{0x10:08x}{self.AdcChannels:02x}{self.AdcRate:02x}"]

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
        return [f"{8:08x}{mask:04x}{val:04x}"]

    def getUsbMsg6(self,bank:int):
        if self.Duty[bank*6:bank*6+6] == ([None] * 6):
            return []
        
        dutymask = 0
        for i in range(6):
            if self.Duty[i+bank*6] != None:
                dutymask |= (1<<i)
        r = f"{6:08x}{bank:02x}{dutymask:02x}"
        for i in range(6): 
            r += f"{self.Duty[i+bank*6] or 0:02x}"
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
        self.RelayStates = [None] * 6        
        
    def setRelay(self, relay: int, state: bool):
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
        return [f"{0x12:08x}{mask:02x}{val:02x}"]

class DiMessage:
    def __init__(self):
        self.dimonitorrate = None 

    def setDiMonitorUpdateRate(self,rate:int):
        self.dimonitorrate = rate

    def get_di_messages(self):
        if self.dimonitorrate == None:
            return []
        return [f"{0xa:08x}{self.dimonitorrate:02x}"]

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
        return [f"{0xc:08x}{self.actmonitorChannels:04x}{self.actmonitorRate:02x}{self.actmonitorThreshold:02x}"]            

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
        return [f"{0xe:08x}{self.freqmonitorChannels:02x}{self.freqmonitorRate:02x}"]          

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
        

    def __init__(self):
        self.callParentInits()
        AdcMessage.__init__(self)
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
        self.actcurrent_listinfirstmsg = None
    def start(self):
        self.dev = usb.core.find(idVendor=0x2B87,idProduct=0x0001)
        if self.dev is None:
            raise ValueError('Device not found')
        threading.Thread(target=self.usbrxhandler,args=([])).start()

    def finished(self):
        print(f"testcubeUSB: finished")
        msgs = (self.get_relay_messages()
            + self.get_pwm_messages()
            + self.get_di_messages()
            + self.get_actcur_messages()
            + self.get_sendusb_messages()
            + self.get_freq_messages()
            + self.get_adc_messages()
        )
        for msg in msgs:
            print(f"testcubeUSB: finished: write({msg=})")
            self.dev.write(2, msg)
        self.callParentInits()

    def usbrxhandler(self):
        time.sleep(2)
        while 1: 
            try:
                msgs = self.dev.read(self.dev[0][(0,0)][0], 100, 1)
            except usb.core.USBError as e:
                if "timeout error" not in str(e):
                    print(f"USB: {e}")
                continue
            print(f"got a USB msg(s)")
            for msg in msgs:
                d = self.recUsb(msg)
                if len(d) > 0:
                    pub.sendMessage('update_received', message = d)
            

    def recUsb(self,msg):
        
        id, payload = msg[:8], msg[8:]
        f = self.usbidparsers.get(id)
        if f is None:
            raise("invalid id")
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
        ret = [{}]*12
        bank,mo,dcf,dce,dcd,dcc,dcb,dca = (
            int(payload[:2],16),
            int(payload[2:4],16),
            int(payload[4:6],16),
            int(payload[6:8],16),
            int(payload[8:10],16),
            int(payload[10:12],16),
            int(payload[12:14],16),
            int(payload[14:16],16)
        )
        ret[6*bank+0] = {'dutyCycle': dca}
        ret[6*bank+1] = {'dutyCycle': dcb}
        ret[6*bank+2] = {'dutyCycle': dcc}
        ret[6*bank+3] = {'dutyCycle': dcd}
        ret[6*bank+4] = {'dutyCycle': dce}
        ret[6*bank+5] = {'dutyCycle': dcf}
        path = '/pwmController/pwms'
        return [{'path': path, 'data': ret}]

    def recusb_9_pwmenable(self,payload):
        d = []
        enabled = int(payload[:4],16)
        data = [{'enabled': True} if (enabled & (1<<x)) else {'enabled': False} for x in range(12)]
        path = '/pwmController/pwms'
        d.append({'path':path,'data':data})
        return d

    def recusb_b_digitalinputs(self,payload):
        d = []
        high = int(payload[:4],16)
        data = [{'high': True} if (high & (1<<x)) else {'high': False} for x in range(12)]
        path = '/digitalInputController/digitalInputs'
        d.append({'path':path,'data':data})
        return d        

    def recusb_00d_actcurrent(self,payload):
        ret = [{}]*12
        payload = payload + "0"*16  #pad to avoid errors
        channels,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )
        #this first msg defines which channels are in subsequent msgs
        self.actcurrent_listinfirstmsg = [i for i in [11,10,9,8,7,6,5,4,3,2,1,0] if (channels & (1<<(i)))]
        thismsg = self.actcurrent_listinfirstmsg[0:3]
        
        for ch,v in zip(thismsg,[cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'currentMonitor':{'measuredCurrent': v}}
        path = '/pwmController/pwms'
        return [{'path': path, 'data': ret}]                

    def recusb_10d_actcurrent(self,payload):
        ret = [{}]*12
        payload = payload + "0"*16  #pad to avoid errors
        cd,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )        
        thismsg = self.actcurrent_listinfirstmsg[3:7]
        for ch,v in zip(thismsg,[cd,cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'currentMonitor':{'measuredCurrent': v}}
        path = '/pwmController/pwms'
        return [{'path': path, 'data': ret}]        

    def recusb_20d_actcurrent(self,payload):
        ret = [{}]*12
        payload = payload + "0"*16  #pad to avoid errors
        cd,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )        
        thismsg = self.actcurrent_listinfirstmsg[7:11]
        for ch,v in zip(thismsg,[cd,cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'currentMonitor':{'measuredCurrent': v}}
        path = '/pwmController/pwms'
        return [{'path': path, 'data': ret}]                
   
    def recusb_30d_actcurrent(self,payload):
        ret = [{}]*12
        payload = payload + "0"*16  #pad to avoid errors
        cd = (
            int(payload[:4],16),
        )        
        thismsg = self.actcurrent_listinfirstmsg[12:]
        print(thismsg)
        for ch,v in zip(thismsg,[cd]):
            if isinstance(ch,int):
                ret[ch] = {'currentMonitor':{'measuredCurrent': v}}
        path = '/pwmController/pwms'
        return [{'path': path, 'data': ret}]                

    def recusb_00f_speed(self,payload):
        ret = [{}]*4
        payload = payload + "0"*16  #pad to avoid errors
        channels,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )
        #this first msg defines which channels are in subsequent msgs
        self.speed_listinfirstmsg = [i for i in [3,2,1,0] if (channels & (1<<(i)))]
        thismsg = self.speed_listinfirstmsg[0:3]
        
        for ch,v in zip(thismsg,[cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'measuredFrequency': v}
        path = '/frequencyInputController/frequencyInputs'
        return [{'path': path, 'data': ret}]                
        

    def recusb_10f_speed(self,payload):
        ret = [{}]*4
        payload = payload + "0"*16  #pad to avoid errors
        cd = int(payload[:4],16)

        thismsg = self.speed_listinfirstmsg[3:]
        
        for ch,v in zip(thismsg,[cd]):
            if isinstance(ch,int):
                ret[ch] = {'measuredFrequency': v}
        path = '/frequencyInputController/frequencyInputs'
        return [{'path': path, 'data': ret}]               
        
    def recusb_011_adc(self,payload):
        ret = [{}]*8
        payload = payload + "0"*16  #pad to avoid errors
        channels,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )
        #this first msg defines which channels are in subsequent msgs
        self.adc_listinfirstmsg = [i for i in [7,6,5,4,3,2,1,0] if (channels & (1<<(i)))]
        thismsg = self.adc_listinfirstmsg[0:3]
        
        for ch,v in zip(thismsg,[cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'measuredVoltage': v}
        path = '/adcInputController/adcInputs'
        return [{'path': path, 'data': ret}]         
        
    def recusb_111_adc(self,payload):
        ret = [{}]*8
        payload = payload + "0"*16  #pad to avoid errors
        cd,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )
        #this first msg defines which channels are in subsequent msgs
        thismsg = self.adc_listinfirstmsg[3:7]
        
        for ch,v in zip(thismsg,[cd,cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'measuredVoltage': v}
        path = '/adcInputController/adcInputs'
        return [{'path': path, 'data': ret}]    
    def recusb_211_adc(self,payload):
        ret = [{}]*8
        payload = payload + "0"*16  #pad to avoid errors
        cd,cc,cb,ca = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16),
            int(payload[12:16],16)
        )
        #this first msg defines which channels are in subsequent msgs
        thismsg = self.adc_listinfirstmsg[7:]
        
        for ch,v in zip(thismsg,[cd,cc,cb,ca]):
            if isinstance(ch,int):
                ret[ch] = {'measuredVoltage': v}
        path = '/adcInputController/adcInputs'
        return [{'path': path, 'data': ret}]        
    
    def recusb_13_relay(self,payload):
        enabled = (
            int(payload[:2],16)
        )
        data = [{'enabled': True} if (enabled & (1<<x)) else {'enabled': False} for x in range(8)]

        path = 'relayController/relays'
        return [{'path': path, 'data': data}]

    def recusb_1d_actfault(self,payload):
        sync,faults = (
            int(payload[:1],16),
            int(payload[1:4],16)
        )
        data = [{'currentMonitor':{'faulty': True}} if (faults & (1<<x)) else {'currentMonitor':{'faulty': False}} for x in range(12)]

        path = 'pwmController/pwms'
        return [{'path': path, 'data': data}]  
                      
    def recusb_41_version(self,payload):
        hi,lo,patch = (
            int(payload[:4],16),
            int(payload[4:8],16),
            int(payload[8:12],16)
        )
        data = f"{hi=}.{lo=}.{patch=}"

        path = 'version'
        return [{'path': path, 'data': data}]  
