class FrequencyMessage:
    def __init__(self):
        self.freqmonitorRate = None
        self.freqmonitorChannels = None

    def setFrequencyInputEnabled(self, freqmask: int):
        self.freqmonitorChannels = freqmask

    def setFrequencyMonitorRate(self, rate):
        self.freqmonitorRate = int(rate/50)

    def get_freq_messages(self):
        if self.freqmonitorRate == None:
            return []
        if self.freqmonitorChannels == None:
            return []
        return [f"{0xe:08x}{self.freqmonitorChannels:02x}{self.freqmonitorRate:02x}"]

    def recusb_00f_speed(self, payload):
        ret = [{}] * 4
        payload = payload + "0" * 16  # pad to avoid errors
        channels, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        # this first msg defines which channels are in subsequent msgs
        self.speed_listinfirstmsg = [i for i in [3, 2, 1, 0] if (channels & (1 << (i)))]
        thismsg = self.speed_listinfirstmsg[0:3]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = {"measuredFrequency": v}
        path = "/frequencyInputController/frequencyInputs"
        return [{"path": path, "data": ret}]

    def recusb_10f_speed(self, payload):
        ret = [{}] * 4
        payload = payload + "0" * 16  # pad to avoid errors
        cd = int(payload[:4], 16)

        thismsg = self.speed_listinfirstmsg[3:]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd]):
            if isinstance(ch, int):
                ret[ch] = {"measuredFrequency": v}
        path = "/frequencyInputController/frequencyInputs"
        return [{"path": path, "data": ret}]
