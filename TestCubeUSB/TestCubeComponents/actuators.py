class ActCurMessage:
    def __init__(self):
        self.actmonitorRate = None
        self.actmonitorChannels = 0x0FFF
        self.actmonitorThreshold = 60

    def setPwmCurrentMonitorUpdateRate(self, rate: int):
        rate = int(rate / 50)
        self.actmonitorRate = rate

    def setPwmFaultThreshold(self, threshold: int):
        threshold = int(threshold / 50)
        self.actmonitorThreshold = threshold

    #    def setPwmFaultDelay(self):

    def setPwmCurrentMonitorChannels(self, channelMask: int):
        self.actmonitorChannels = channelMask

    def get_actcur_messages(self):
        if self.actmonitorChannels == None:
            return []
        if self.actmonitorRate == None:
            return []
        if self.actmonitorThreshold == None:
            return []
        return [
            f"{0xc:08x}{self.actmonitorChannels:04x}{self.actmonitorRate:02x}{self.actmonitorThreshold:02x}"
        ]
