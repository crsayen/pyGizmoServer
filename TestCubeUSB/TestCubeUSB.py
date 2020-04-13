import usb.core
import usb.util
import asyncio
from pyGizmoServer.controller import Controller
from TestCubeUSB.TestCubeComponents.adc import AdcMessage
from TestCubeUSB.TestCubeComponents.pwm import PwmMessage
from TestCubeUSB.TestCubeComponents.relay import RelayMessage
from TestCubeUSB.TestCubeComponents.di import DiMessage
from TestCubeUSB.TestCubeComponents.actuators import ActCurMessage
from TestCubeUSB.TestCubeComponents.frequency import FrequencyMessage
from TestCubeUSB.TestCubeComponents.usb import UsbMessage
from TestCubeUSB.TestCubeComponents.can import CanDatabaseMessage
from TestCubeUSB.TestCubeComponents.version import VersionMessage
from pyGizmoServer.utility import debug
import time


class TestCubeUSB(
    Controller,
    RelayMessage,
    PwmMessage,
    DiMessage,
    ActCurMessage,
    UsbMessage,
    FrequencyMessage,
    AdcMessage,
    CanDatabaseMessage,
    VersionMessage,
):
    def reset_parents(self):
        self.resetRelayMessage()
        self.resetPwmMessage()
        self.resetDiMessage()
        self.resetActCurMessage()
        UsbMessage.__init__(self)
        self.resetFrequencyMessage()
        self.resetAdcMessage()
        self.resetVersionMessage()

    def __init__(self):
        debug("init")
        Controller.__init__(self)
        RelayMessage.__init__(self)
        PwmMessage.__init__(self)
        DiMessage.__init__(self)
        ActCurMessage.__init__(self)
        UsbMessage.__init__(self)
        FrequencyMessage.__init__(self)
        AdcMessage.__init__(self)
        VersionMessage.__init__(self)
        self.version = None
        self.ask = None
        self.usbrxcount = 0
        self.usbidparsers = {
            "00000005": self.rec_usb_5_pwmfreq,
            "00000007": self.rec_usb_7_pwmdutycycle,
            "00000009": self.rec_usb_9_pwmenable,
            "0000000b": self.rec_usb_b_digitalinputs,
            "0000000d": self.rec_usb_00d_actcurrent,
            "0000010d": self.rec_usb_10d_actcurrent,
            "0000020d": self.rec_usb_20d_actcurrent,
            "0000030d": self.rec_usb_30d_actcurrent,
            "0000000f": self.rec_usb_00f_speed,
            "0000010f": self.rec_usb_10f_speed,
            "00000011": self.rec_usb_011_adc,
            "00000111": self.rec_usb_111_adc,
            "00000211": self.rec_usb_211_adc,
            "00000013": self.rec_usb_13_relay,
            #"0000001d": self.rec_usb_1d_actfault,
            "00000051": self.rec_usb_51_version,
            "0000001b": self.rec_1b_pwmProfileDuty,
            "0000011b": self.rec_11b_pwmProfileDuty,
            "0000021b": self.rec_21b_pwmProfileIndex,
            "0000031b": self.rec_31b_pwmProfileIndex,
            "0000041b": self.rec_41b_pwmProfileIndex,
            "0000051b": self.rec_51b_pwmProfileFrequency,
        }
        self.actcurrent_listinfirstmsg = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        self.adc_listinfirstmsg = []

    def setup(self):
        self.dev = None
        devs = usb.core.find(idVendor=0x2B87, idProduct=0x0001, find_all=True)
        if devs is not None:
            for dev in devs:
                dev.write(2, "0000050")
                self.dev = dev
                d = str(dev).split("\n")
                devdict = {}
                for line in d:
                    if "DEVICE ID" in line:
                        s = line.split(" ")
                        devdict["deviceid"] = s[2]
                        devdict["bus"] = s[5] + "." + s[7]
                    elif ":" in line:
                        k, v = line.split(":")[0].strip(), line.split(":")[1].strip()
                        devdict[k] = v
                self.send("/usb/usbinfo", devdict)
                self.spawnPeriodicTask(self.readActFaults, args=[], period=0.2)
                return
        raise ValueError("Device not found")

    def finished_processing_request(self):
        debug(f"finished")
        msgs = self.get_relay_messages()
        msgs += self.get_pwm_messages()
        msgs += self.get_di_messages()
        msgs += self.get_actcur_messages()
        msgs += self.get_sendusb_messages()
        msgs += self.get_freq_messages()
        msgs += self.get_adc_messages()
        msgs += self.get_version_messages()
        debug(f"\n{msgs=}")
        for i,msg in enumerate(msgs):
            print(msg)
            self.dev.write(2, msg)
            if i % 10 == 9: time.sleep(0.001)
        self.reset_parents()

    async def do(self):
        try:
            msg = self.dev.read(130, 24, 1)
        except usb.core.USBError:
            return
        msg = "".join([chr(x) for x in msg])
        debug(f"{msg=}")
        self.usbrxcount += 1
        self.send( updates =
            [
                {"path": "/usb/rxMessage", "data": msg},
                {"path": "/usb/rxCount", "data": self.usbrxcount},
            ]
        )

        d = self.rec_usb(msg)
        if d is None:
            return
        if len(d) > 0:
            self.send(updates = d)

    async def heartbeat(self):
        if await self.getFirmwareVersion():
            return True
        return False

    def rec_usb(self, msg):
        _id, payload = msg[:8], msg[8:]
        try:
            f = self.usbidparsers.get(_id.lower())
            debug(f"usbidparsers.get({_id}): {f}")
            if f is None:
                return []
        except Exception:
            pass
        if f is None:
            return []
        result = f(payload)
        debug(f"{result=}\n")
        return result

    async def readActFaults(self):
        self.dev.write(2,'0000000800007fff')