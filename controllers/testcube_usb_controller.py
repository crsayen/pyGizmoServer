import usb.core
from usb.backend import libusb1
import usb.util
import time


class RelayMessage:
    def __init__(self):
        self.states = [None,None,None,None,None,None]        
        
    def setstate(self, relay, state):
        self.states[relay] = state

    def get_message_string(self):
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

