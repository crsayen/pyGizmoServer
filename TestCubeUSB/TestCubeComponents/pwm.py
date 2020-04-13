from pyGizmoServer.utility import debug, Error, logError
import re
import os

class PwmMessage:
    def __init__(self):
        self.Freq = [None] * 2
        self.Hiconf = [None] * 12
        self.PwmEnabled = [None] * 12
        self.Duty = [None] * 12
        self.profileIndecies = [None] * 12
        self.pwmStartMessage = []
        self.pwmPauseMessage = []
        self.pwmStopMessage = []
        self.profileEntries = []
        self.suppToBeEnPwms = [None] * 12
        self.pwmProfileUpdatesMessage = []
        self.pwmFaults = [False] * 12
        self.expectPwmMsg = False

    def resetPwmMessage(self):
        self.pwmStartMessage = []
        self.expectPwmMsg = False
        self.pwmPauseMessage = []
        self.pwmStopMessage = []
        self.profileEntries = []
        self.pwmProfileUpdatesMessage = []

    def setPwmFrequencyA(self, hz: int):
        self.expectPwmMsg = True
        self.Freq[0] = hz

    def setPwmFrequencyB(self, hz: int):
        self.expectPwmMsg = True
        self.Freq[1] = hz

    def sethiconf(self, idx: int, activehi: str):
        self.expectPwmMsg = True
        if activehi.upper() == "HIGH":
            activehi = True
        elif activehi.upper() == "LOW":
            activehi = False
        else:
            raise ValueError("active configuration must be either high or low")
        self.Hiconf[idx] = activehi

    def setPwmDutyCycle(self, idx: int, duty: int):
        self.expectPwmMsg = True
        self.Duty[idx] = duty

    def setPwmEnabled(self, idx: int, enabled: bool):
        self.expectPwmMsg = True
        self.suppToBeEnPwms[idx] = enabled
        self.PwmEnabled[idx] = enabled

    def getUsbMsg8(self):
        if self.PwmEnabled == [None] * 12 or not self.expectPwmMsg:
            return []
        mask = 0
        val = 0
        for i in range(0, len(self.PwmEnabled)):
            if self.PwmEnabled[i] != None:
                mask |= 1 << i
                if self.PwmEnabled[i]:
                    val |= 1 << i
        return [f"{8:08x}{mask:04x}{val:04x}"]

    def getUsbMsg6(self, bank: int):
        if self.Duty[bank * 6 : bank * 6 + 6] == ([None] * 6) or not self.expectPwmMsg:
            return []

        dutymask = 0
        for i in range(6):
            if self.Duty[i + bank * 6] != None:
                dutymask |= 1 << i
        r = f"{6:08x}{bank:02x}{dutymask:02x}"
        for i in reversed(range(6)):
            r += f"{self.Duty[i+bank*6] or 0:02x}"
        return [r]

    def getUsbMsg4(self):
        if (self.Freq == [None] * 2) and (self.Hiconf == [None] * 12) or not self.expectPwmMsg:
            return []
        freqmask = 0x0
        hilomask = 0x000
        hiloval = 0x000
        for i in range(0, len(self.Freq)):
            if self.Freq[i] != None:
                freqmask |= 8 >> i

        for i in range(0, len(self.Hiconf)):
            if self.Hiconf[i] != None:
                hilomask |= 1 << i
                if self.Hiconf[i]:
                    hiloval |= 1 << i

        try:
            assert freqmask <= 0xF
            assert hilomask <= 0xFFF
            assert hiloval <= 0xFFF
        except:
            raise ValueError("PwmMessageFieldOverflow")

        r = "{:08x}{:01x}{:03x}0{:03x}{:04x}{:04x}".format(
            0x04, freqmask, hilomask, hiloval, self.Freq[0] or 0, self.Freq[1] or 0
        )
        return [r]

    def get_pwm_messages(self):
        msgs = (
            self.getUsbMsg4()
            + self.getUsbMsg6(0)
            + self.getUsbMsg6(1)
            + self.getUsbMsg8()
            + self.pwmStartMessage
            + self.pwmStopMessage
            + self.pwmPauseMessage
            + self.profileEntries
            + self.pwmProfileUpdatesMessage
        )
        self.expectPwmMsg = False
        debug(msgs)
        return msgs

    def rec_usb_5_pwmfreq(self, payload):
        acthi, freqa, freqb = payload[:4], payload[4:8], payload[8:12]
        d = []
        path = "/pwmController/bankA/frequency"
        data = int(freqa, 16)
        d.append({"path": path, "data": data})
        path = "/pwmController/bankB/frequency"
        data = int(freqb, 16)
        d.append({"path": path, "data": data})
        path = "/pwmController/pwms"
        data = [
            {"activeConfiguration": "high"}
            if (int(acthi, 16) & (1 << x))
            else {"activeConfiguration": "low"}
            for x in range(12)
        ]
        d.append({"path": path, "data": data})
        return d

    def rec_usb_7_pwmdutycycle(self, payload):
        pass
        # self.dutyFromPayload(payload)
        # if payload[:2] == '01':
        #     path = "/pwmController/pwms"
        #     return [{"path": path, "data": [{"dutyCycle": dc} for dc in self.Duty]}]

    def rec_usb_9_pwmenable(self, payload):
        d = []
        enabled = int(payload[:4], 16)
        data = [
            {"enabled": True} if (enabled & (1 << x)) else {"enabled": False}
            for x in range(12)
        ]
        for i, en in enumerate(data):
            self.PwmEnabled[i] = en["enabled"]
            if self.suppToBeEnPwms[i] is None:
                continue
            self.pwmFaults[i] = self.suppToBeEnPwms[i] and not en["enabled"]
        self.send(f"/pwmController/faults", self.pwmFaults)
        path = "/pwmController/pwms"
        d.append({"path": path, "data": data})
        return d

    def uploadPwmProfile(self, path):
        try:
            with open(path, "r") as f:
                profileEntries = [line for line in f if line.startswith('00000014')]
        except Exception as e:
            return Error(f"failed to upload profile at: {path}\n{e}")
        self.profileEntries = profileEntries

    def startPwmProfile(self, index):
        self.pwmStartMessage = ["00000016{:03x}".format(1 << index)]

    def pausePwmProfile(self, index):
        self.pwmPauseMessage = ["00000017{:03x}".format(1 << index)]

    def stopPwmProfile(self, index):
        self.pwmStopMessage = ["00000018{:03x}".format(1 << index)]

    def createProfileMessageFromMask(self, _id, mask):
        if len(mask) != 3:
            logError(f"invalid mask: {mask}")
            return []
        try:
            int(mask, 16)
        except ValueError:
            logError(f"invalid mask: {mask}")
            return []
        msg = ["000000{}{}".format(_id, mask)]
        debug(msg)
        return msg

    def startPwmProfiles(self, mask):
        self.pwmStartMessage = self.createProfileMessageFromMask("16", mask)

    def pausePwmProfiles(self, mask):
        self.pwmPauseMessage = self.createProfileMessageFromMask("17", mask)

    def stopPwmProfiles(self, mask):
        self.pwmStopMessage = self.createProfileMessageFromMask("18", mask)

    def enablePwmProfileUpdates(self, enabled):
        payload = '01' if enabled else '00'
        self.pwmProfileUpdatesMessage = [f'0000001A{payload}']

    ##############################################################################
    ''' Duty Cycle - PWM profile '''
    ##############################################################################

    def dutyFromPayload(self, payload, start, stop):
        chunks = (
            int(payload[:2], 16),
            int(payload[2:4], 16),
            int(payload[4:6], 16),
            int(payload[6:8], 16),
            int(payload[8:10], 16),
            int(payload[10:12], 16),
            int(payload[12:14], 16),
            int(payload[14:16], 16),
        )
        self.Duty[start:stop] = chunks[:1:-1]

    def sendIfAllDutyMsgsRcvd(self):
        debug(self.Duty)
        if all([1 if dc is not None  else 0 for dc in self.Duty]):
            out = self.Duty.copy()
            self.Duty = [None] * 12
            path = "/pwmController/profiles/dutyCycles"
            return [{"path": path, "data": out}]
        return []

    def rec_1b_pwmProfileDuty(self, payload):
        self.dutyFromPayload(payload, 0, 6)
        return self.sendIfAllDutyMsgsRcvd()

    def rec_11b_pwmProfileDuty(self, payload):
        self.dutyFromPayload(payload, 6, 12)
        return self.sendIfAllDutyMsgsRcvd()

    ##############################################################################
    ''' Index - PWM profile '''
    ##############################################################################

    def indexFromPayload(self, payload, start, end):
        chunks = (
            int(payload[:2], 16),
            int(payload[2:4], 16),
            int(payload[4:6], 16),
            int(payload[6:8], 16)
        )
        self.profileIndecies[start:end] = chunks

    def sendIfAllIndexMsgsRcvd(self):
        debug(self.profileIndecies)
        if all([1 if i is not None  else 0 for i in self.profileIndecies]):
            out = self.profileIndecies.copy()
            self.profileIndecies = [None] * 12
            path = "/pwmController/profiles/indecies"
            return [{"path": path, "data": out}]
        return []

    def rec_21b_pwmProfileIndex(self, payload):
        self.indexFromPayload(payload, 0, 4)
        return self.sendIfAllIndexMsgsRcvd()

    def rec_31b_pwmProfileIndex(self, payload):
        self.indexFromPayload(payload, 4, 8)
        return self.sendIfAllIndexMsgsRcvd()

    def rec_41b_pwmProfileIndex(self, payload):
        self.indexFromPayload(payload, 8, 12)
        return self.sendIfAllIndexMsgsRcvd()

    ##############################################################################
    ''' Frequency - PWM profile '''
    ##############################################################################

    def rec_51b_pwmProfileFrequency(self, payload):
        return [
            {
                "path": "/pwmController/profiles/frequencies",
                "data": [
                    int(payload[:2], 16),
                    int(payload[2:4], 16)
                ]
            }
        ]