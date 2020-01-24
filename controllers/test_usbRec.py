from controllers.testcube_usb_controller import *
from pyGizmoServer.utility import Utility
from tests.mock_variables import MockVars

class test_usbRec(TestCubeUSB):
    def __init__():
        self.mockvars = MockVars()
        usbidparsers = {'00000005':recusbpwm}
        pass

    def setupModel(self):
        #done somewhere else
        pass

    def test_usbmsg5(self):
        msg = "{:08x}{:04x}{04x}{04x}".format(
            id = 0x5,
            acthi = 0x555,
            freqa = 0x1000,
            freqb = 0xfff
        )

        d = recUsb(msg)

"""         expList = [
            {
                'path'='/pwmController/bankA/frequency',
                'data'=0x1000
            },
            {
                'path'='/pwmController/bankB/frequency',
                'data'=0xFFF
            },
            {
                'path'='/pwmController/pwms',
                'data'= [
                    {"activeConfiguration" : "HIGH"},
                    {"activeConfiguration" : "LOW"}
                ] *6
            }
        ] """
        for pd in d
            results = Utility.parse_path_against_schema_and_model(pd.path,self.mockvars.mock_schema)
            result["model_data"]
            results["data"]
            checkmatchesschema()
            check pd.data = expList[pd.data]

    def test_usbmsg7(self):
        msg = "{:08x}{:02x}{02x}{02x}{02x}{02x}{02x}{02x}{02x}".format(
            id = 7,
            bank = 0x0,
            mod = 0x3f,
            dcf = 0x6,
            dce = 0x5,
            dcd = 0x4,
            dcc = 0x3,
            dcb = 0x2,
            dca = 0x1
        )        
        RecUSB(msg)
     
        # assert(dc = [1,2,3,4,5,6])

        msg = "{:08x}{:02x}{02x}{02x}{02x}{02x}{02x}{02x}{02x}".format(
            id = 7,
            bank = 0x1,
            mod = 0x3f,
            dcf = 0x6,
            dce = 0x5,
            dcd = 0x4,
            dcc = 0x3,
            dcb = 0x2,
            dca = 0x1
        )        
        RecUSB(msg)

    def test_usbmsg9(self):
        msg = "{:08x}{:04x}".format(
            id = 9,
            enablemask = 0x555
        )

    def test_usbmsgb(self):
        msg = "{:08x}{:04x}".format(
            id = 0xb,
            digitalinputs = 0x555
        )
    
    def test_usbmsgd(self): #act curr
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id = 0xd,
            mask = 0xfff,
            a12 = 12,
            a11 = 11,
            a10 = 10
        )

        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id = 0x10d,
            a9 = 9,
            a8 = 8,
            a7 = 7,
            a6 = 6
        )
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id = 0x20d,
            a5 = 5,
            a4 = 4,
            a3 = 3,
            a2 = 2
        )
        msg = "{:08x}{:04x}".format(
            id = 0x30d,
            a1 = 1
        )

    def test_usbf(self): #speed
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id = 0xf,
            mask = 0xf,
            f4 = 4,
            f3 = 3,
            f2 = 2
        )

        msg = "{:08x}{:04x}".format(
            id = 0x10f,
            f1 = 1
        )

    def test_usb11(self): #adc
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id = 0x11,
            mask = 0xf,
            a8 = 8,
            a7 = 7,
            a6 = 6
        )     
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id = 0x211,
            a5 = 5,
            a4 = 4,
            a3 = 3,
            a2 = 2           
        )
        msg = "{:08x}{:04x}".format(
            id = 0x211,
            a1 = 1
        )

    def test_usb13(self): #relay
        msg = "{:08x}{:04x}".format(
            id = 0x13,
            relays = 0x15
        )

    def test_usb1d(self): #act fault
        msg = "{:08x}{:01x}{:03x}".format(
            id = 0x1d,
            sync = 0,
            faults = 0x555
        )

        