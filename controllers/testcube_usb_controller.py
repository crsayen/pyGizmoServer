import usb.core
from usb.backend import libusb1
import usb.util
import time


class RelayMessage:
    def __init__(self):
        self.states = [None,None,None,None,None,None]

    def setstate(self, relay, state):
        self.states[relay] = state
        print(self.states)

    def get_message_string(self):
        return "00000012FF00"

class TestCubeUSB:
    def __init__(self):
        self.messages = {
            "relay": None,
            "pwm": None
        }

    def start(self):
        #be = libusb1.get_backend()
        self.dev = usb.core.find(idVendor=0x2B87,idProduct=0x0001)
        if self.dev is None:
            raise ValueError('Device not found')
        self.dev.set_configuration()
        # try:
        #     self.dev.set_interface_altsetting(interface=0,alternate_setting=0)
        # except Exception as e:
        #     print(f"{e}")

    def setRelay(self, relay, state):
        if self.messages["relay"] is None:
            self.messages["relay"] = RelayMessage()
        msg = self.messages["relay"]
        print(f"stat: {state} Rel: {relay}")
        msg.setstate(relay, state)

    def xmit(self):
        for m in self.messages:
            if self.messages[m] is not None:
                self.dev.write(2,self.messages[m].get_message_string())
                # make a USB message and send it
                self.messages[m] = None

