import asyncio
from TestCubeUSB.getter import get
from pyGizmoServer.utility import Error, repeatOnFailAsync


class AdcMessage:
    def __init__(self):
        self.AdcChannels = 0xFF
        self.AdcRate = None
        self.getAdcVoltageEvent = asyncio.Event()
        self.adcVoltages = [None, None, None, None, None, None, None, None]
        self.expectAdcMsg = False

    def resetAdcMessage(self):
        self.expectAdcMsg = False
        pass

    def setAdcMonitorUpdateRate(self, rate: int):
        self.expectAdcMsg = True
        self.AdcRate = int(rate / 50)

    def setAdcEnabled(self, enabled: bool, channel: int):
        self.expectAdcMsg = True
        if enabled:
            self.AdcChannels |= 1 << channel
        else:
            self.AdcChannels &= (1 << channel) ^ 0xFF

    async def getAdcVoltage(self, index):
        ret = await repeatOnFailAsync(5, self._getAdcVoltage, [index])
        if ret is not None:
            return ret
        return Error("Failed to read actuator current")

    async def _getAdcVoltage(self, index):
        if self.AdcRate:
            return self.adcVoltages[index]
        else:
            self.AdcRate = 0
            # self.finished_processing_request()
            if await get(self.finished_processing_request, self.getAdcVoltageEvent):
                return self.adcVoltages[index]

    def get_adc_messages(self):
        if self.AdcChannels is None or self.AdcRate is None:
            return []
        return [f"{0x10:08x}{self.AdcChannels:02x}{self.AdcRate:02x}"]

    def parse_adc_message(
        self, start, end, payload, chunks, firstMessage=False, lastMessage=False
    ):
        payload = payload + "0" * 16  # pad to avoid errors
        payloadChunks = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        chunks = [payloadChunks[i] for i in chunks]
        # this first msg defines which channels are in subsequent msgs
        if firstMessage:
            self.adc_listinfirstmsg = [
                i for i in [7, 6, 5, 4, 3, 2, 1, 0] if (payloadChunks[0] & (1 << (i)))
            ]
        thismsg = self.adc_listinfirstmsg[start:end]
        if thismsg is not None:
            for ch, v in zip(thismsg, chunks):
                if isinstance(ch, int):
                    self.adcVoltages[ch] = v
            if self.adc_listinfirstmsg[end:] is None or lastMessage:
                if not self.getAdcVoltageEvent.is_set():
                    self.getAdcVoltageEvent.set()
                return [
                    {
                        "path": "/adcInputController/adcInputVoltages",
                        "data": self.adcVoltages,
                    }
                ]

    def rec_usb_011_adc(self, payload):
        return self.parse_adc_message(0, 3, payload, [1, 2, 3], firstMessage=True)

    def rec_usb_111_adc(self, payload):
        return self.parse_adc_message(3, 7, payload, [0, 1, 2, 3])

    def rec_usb_211_adc(self, payload):
        return self.parse_adc_message(7, 12, payload, [0, 1, 2, 3], lastMessage=True)
