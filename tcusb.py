import usb.core
from usb.backend import libusb1
import usb.util
import time

class TestCubeUSB:
    def __init__(self):
        print("init")

    def start(self):
        #be = libusb1.get_backend()
        self.dev = usb.core.find(idVendor=0x2B87,idProduct=0x0001)
        if self.dev is None:
            raise ValueError('Device not found')
        self.dev.set_configuration(1)
        try:
            self.dev.set_interface_altsetting(interface=0,alternate_setting=0)
        except Exception as e:
            print(f"{e}")

    def setRelay(self, relay, state):
        self.dev.write(2,b'\00\x00\x00\x50')
        print(self.dev.read(130,1,timeout=1000))


def main():
    tc = TestCubeUSB()
    tc.start()
    tc.setRelay(0,0)

if __name__ == "__main__":
    main()
