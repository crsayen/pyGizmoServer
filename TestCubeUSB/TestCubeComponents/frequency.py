import asyncio
from TestCubeUSB.getter import get
from pyGizmoServer.utility import Error, repeatOnFailAsync


class FrequencyMessage:
    def __init__(self):
        self.freqmonitorRate = None
        self.speed_listinfirstmsg = [3, 2, 1, 0]
        self.freqmonitorChannels = [1, 1, 1, 1]
        self.getFrequencyEvent = asyncio.Event()
        self.frequencies = [None, None, None, None]
        self.expectFreqMsg = False

    def resetFrequencyMessage(self):
        self.speed_listinfirstmsg = [3, 2, 1, 0]
        self.freqmonitorChannels = [1, 1, 1, 1]
        self.expectFreqMsg = False
        self.frequencies = [None, None, None, None]

    def setFrequencyInputEnabled(self, channel: int, enabled: int):
        self.expectFreqMsg = True
        self.freqmonitorChannels[channel] = enabled

    def setFrequencyMonitorRate(self, rate):
        self.expectFreqMsg = True
        self.freqmonitorRate = int(rate / 50)

    async def getFrequency(self, index):
        ret = await repeatOnFailAsync(5, self._getFrequency, [index])
        if ret is not None:
            return ret
        return Error("Failed to read frequency")

    async def _getFrequency(self, index):
        if self.freqmonitorRate:
            return self.frequencies[index]
        else:
            self.freqmonitorRate = 0
            # self.finished_processing_request()
            if await get(self.finished_processing_request, self.getFrequencyEvent):
                return self.frequencies[index]

    def get_freq_messages(self):
        if self.freqmonitorRate is None or self.freqmonitorChannels is None:
            return []
        channels = "".join(["1" if i else "0" for i in self.freqmonitorChannels])
        # print(channels)
        channels = int(channels[::-1], 2)
        return [f"{0xe:08x}{channels:02x}{self.freqmonitorRate:02x}"]

    def rec_usb_00f_speed(self, payload):
        payload = payload + "0" * 16  # pad to avoid errors
        channels, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        # this first msg defines which channels are in subsequent msgs
        self.speed_listinfirstmsg = [i for i in [3, 2, 1, 0] if (channels & (1 << (i)))]
        if self.speed_listinfirstmsg[0:3] is not None:
            for ch, v in zip(self.speed_listinfirstmsg[0:3], [cc, cb, ca]):
                if isinstance(ch, int):
                    self.frequencies[ch] = v
            if self.speed_listinfirstmsg[3:] is None:
                if not self.getFrequencyEvent.is_set():
                    self.getFrequencyEvent.set()
                return [
                    {
                        "path": "/frequencyInputController/measuredFrequencies",
                        "data": self.frequencies,
                    }
                ]

    def rec_usb_10f_speed(self, payload):
        payload = payload + "0" * 16  # pad to avoid errors
        cd = int(payload[:4], 16)
        if self.speed_listinfirstmsg[3:] is not None:
            for ch, v in zip(self.speed_listinfirstmsg[3:], [cd]):
                if isinstance(ch, int):
                    self.frequencies[ch] = v
            if not self.getFrequencyEvent.is_set():
                self.getFrequencyEvent.set()
            return [
                {
                    "path": "/frequencyInputController/measuredFrequencies",
                    "data": self.frequencies,
                }
            ]
