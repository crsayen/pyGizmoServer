import usb.core
from usb.backend import libusb1
import usb.util
import time


class PwmMessage:
    def __init__(self):
        self.Freq = [None] * 2
        self.Hiconf = [None] * 12

        self.Enabled = [None] * 12
        self.Duty = [None] * 12
        
    def setfreq(self, bank: int, hz: int):
        self.Freq[bank] = hz

    def sethiconf(self, idx: int, activehi: bool):
        self.Hiconf[idx] = activehi

    def setduty(self, idx: int, duty: int):
        self.Duty[idx] = duty

    def setenabled(self, idx: int, enabled: bool):
        self.Enabled[idx] = enabled

    def getUsbMsg8(self):
        if self.Enabled == [None] * 12:
            return None
        mask = 0
        val = 0
        for i in range(0,len(self.Enabled)): 
            if self.Enabled[i] != None:
                mask |= (1<<i)
                if self.Enabled[i]:
                    val |= (1<<i)           
        r = "{:08x}{:04x}{:04x}".format(
            0x08,mask,val)
        return r
        
    def getUsbMsg6(self,bank:int):
        if self.Duty[bank*6:bank*6+6] == ([None] * 6):
            return None
        
        dutymask = 0
        for i in range(6):
            if self.Duty[i+bank*6] != None:
                dutymask |= (1<<i)
        r = "{:08x}{:02x}{:02x}".format(
            0x06,bank,dutymask) 
        for i in range(6): 
            r += "{:02x}".format(self.Duty[i+bank*6] or 0) 
        return r           
                    

    def getUsbMsg4(self):
        if (self.Freq == [None]*2) and (self.Hiconf == [None]*12):
            return None
        freqmask=0x0
        hilomask=0x000
        hiloval=0x000
        for i in range(0,len(self.Freq)): 
            if self.Freq[i] != None:
                freqmask |= (1<<i+2)

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
        return r


    def get_message_string(self):
        return self.getUsbMsg4()

class RelayMessage:
    def __init__(self):
        self.states = [None,None,None,None,None,None]        
        
    def setstate(self, relay, state):
        self.states[relay] = state

    def get_message_string(self):
        if self.states == [None] * 6:
            return None
        mask = 0
        val = 0
        for i in range(0,len(self.states)): 
            if self.states[i] != None:
                mask |= (1<<i)
                if self.states[i]:
                    val |= (1<<i)   
        r = "{:08x}{:02x}{:02x}".format(0x12,mask,val)
        return r

class TestCubeUSB:
    def __init__(self):
        self.messages = {
            "relay": None,
            "pwm": None
        }

    def start(self):
        self.dev = usb.core.find(idVendor=0x2B87,idProduct=0x0001)
        if self.dev is None:
            raise ValueError('Device not found')
        self.dev.set_configuration()

    def setRelay(self, relay, state):
        if self.messages["relay"] is None:
            self.messages["relay"] = RelayMessage()
        msg = self.messages["relay"]
        msg.setstate(relay, state)

    def xmit(self):
        for key, value in self.messages.items():
            if value is not None:
                self.dev.write(2, value.get_message_string())
                self.messages[key] = None

