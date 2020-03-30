import asyncio

class ActCurMessage:
    def __init__(self):
        self.actmonitorRate = None
        self.actmonitorChannels = 0x0FFF
        self.actmonitorThreshold = 60
        self.ret = [None] * 12

    def resetActCurMessage(self):
        self.ret = [None] * 12

    def setPwmCurrentMonitorUpdateRate(self, rate: int):
        rate = int(rate / 50)
        self.actmonitorRate = rate

    def setPwmFaultThreshold(self, threshold: int):
        self.actmonitorThreshold = int(threshold / 50)

    def setPwmCurrentMonitorChannels(self, channelMask: int):
        self.actmonitorChannels = channelMask

    async def getFaultMonitors(self, retry=0):
        self.getFaults = True
        self.finished_processing_request()
        if self.getFaultsEvent is None:
            self.getFaultsEvent = asyncio.Event()
        else:
            self.getFaultsEvent.clear()
        try:
            await asyncio.wait_for(self.getFaultMonitors.wait(), timeout=0.1)
        except:
            if retry < 5:
                return await self.getFaultsEvent(retry = retry + 1)
            raise RuntimeError("getFaultMonitors not responding")
        return self.actFaults

    async def getFaultMonitor(self, index, retry=0):
        self.getFaults = True
        self.finished_processing_request()
        if self.getFaultsEvent is None:
            self.getFaultsEvent = asyncio.Event()
        else:
            self.getFaultsEvent.clear()
        try:
            await asyncio.wait_for(self.getFaultsEvent.wait(), timeout=0.1)
        except:
            if retry < 5:
                return await self.getFaultMonitor(index, retry = retry + 1)
            raise RuntimeError("getFaultMonitor not responding")
        return self.actFaults[index]

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

    def get_actuator_faults(self):
        if self.getFaults is True:
            self.getFaults = False
        return ["0000001c0000"]

    def rec_usb_1d_actfault(self, payload):
        print(payload)
        _, faults = (int(payload[:1], 16), int(payload[1:4], 16))
        self.actFaults = [True if (faults & (1 << x)) else False for x in range(12)]
        print(self.actFaults)
        if self.getFaultsEvent is not None and not self.getFaultsEvent.is_set():
            self.getFaultsEvent.set()
        return [{"path": "/pwmController/faultMonitors", "data": self.actFaults}]

    def rec_usb_00d_actcurrent(self, payload):
        ret = [None] * 12
        self.ret = ret
        payload = payload + "0" * 16  # pad to avoid errors
        channels, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        # this first msg defines which channels are in subsequent msgs
        self.actcurrent_listinfirstmsg = [
            i for i in [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0] if (channels & (1 << (i)))
        ]
        thismsg = self.actcurrent_listinfirstmsg[0:3]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        if self.actcurrent_listinfirstmsg[3:] is None:
            return [{"path": path, "data": ret}]
        else:
            self.ret = ret

    def rec_usb_10d_actcurrent(self, payload):
        ret = self.ret
        if len(ret) < 12:
            ret = [None] * (12 - len(ret)) + ret
        payload = payload + "0" * 16  # pad to avoid errors
        cd, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        thismsg = self.actcurrent_listinfirstmsg[3:7]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd, cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        if self.actcurrent_listinfirstmsg[7:] is None:
            return [{"path": path, "data": ret}]
        else:
            self.ret = ret

    def rec_usb_20d_actcurrent(self, payload):
        ret = self.ret
        if len(ret) < 12:
            ret = [None] * (12 - len(ret)) + ret
        payload = payload + "0" * 16  # pad to avoid errors
        cd, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        thismsg = self.actcurrent_listinfirstmsg[7:11]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd, cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        if self.actcurrent_listinfirstmsg[11:] is None:
            return [{"path": path, "data": ret}]
        else:
            self.ret = ret

    def rec_usb_30d_actcurrent(self, payload):
        ret = self.ret
        if len(ret) < 12:
            ret = [None] * (12 - len(ret)) + ret
        ret = self.ret
        payload = payload + "0" * 16  # pad to avoid errors
        cd = int(payload[:4], 16)
        thismsg = self.actcurrent_listinfirstmsg[11:]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        return [{"path": path, "data": ret}]