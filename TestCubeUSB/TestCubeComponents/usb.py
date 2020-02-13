class UsbMessage:
    def __init__(self):
        self.usbmsg = None

    def sendrawusb(self, msg):
        self.usbmsg = msg

    def get_sendusb_messages(self):
        if self.usbmsg is None:
            return []
        return [self.usbmsg]
