from controllers.testcube_usb_controller import *
from pyGizmoServer.utility import Utility
from tests.mock_variables import MockVars

class Test_usbRec():

    def checkmatch(self,md,pd,loc):
        #print("pd type " + str(type(pd)))
        #print("md type " + str(type(md)))
        #print('cdm')
        #print(pd)
        #print(md)
        #print(type(pd),type(md))

        if isinstance(md,list):
            idx=0
            for m,p in zip(md,pd):
                #print('break up list')
                self.checkmatch(m,p,loc + f'[{idx}]')
                idx = idx + 1
        elif isinstance(md,dict): 
            #print('dict')              
            for k,v in pd.items(): #the model can have more stuff than in the usb msg
                #print(k,v)
                assert(k in md.keys()),f"usb parse to place not in model {loc=}/{k} {idx=}"
                #self.checkdatamatch(m,p,"recursion" + str(k))
                #print('break up dict')
                self.checkmatch(md[k],v,loc + '/' + k)
                #assert (v == m[k]),f"value doesn't match model {loc=}/{k} {idx=}"
            #idx=idx+1
        else:
            assert(md == pd),f"{loc=}"



    def processandcheck(self,msg):
        d = self.controller.recUsb(msg)
    
        for pd in d:
            #print('pd ' + str(pd))
            results = Utility.parse_path_against_schema_and_model(path=pd['path'],schema=self.mockvars.mock_schema,model=self.mockvars.mock_model)
            print(results)
            self.checkmatch(results['model_data'],pd['data'],pd['path'])


    def setup(self):
        self.mockvars = MockVars()
        self.controller=TestCubeUSB()
        #print('mockModel ' + str(self.mockvars.mock_model))
        pass

    def test_usbmsg5(self): #pwm act and freq
        self.setup()
        id = 0x5
        acthi = 0x555
        freqa = 0x1000
        freqb = 0xfff

        msg = '{:08x}{:04x}{:04x}{:04x}'.format(id,acthi,freqa,freqb)
        self.processandcheck(msg) 

    def test_usbmsg7(self):
        id = 7
        bank = 0x0
        mod = 0x3f
        dcf = 0x6
        dce = 0x5
        dcd = 0x4
        dcc = 0x3
        dcb = 0x2
        dca = 0x1
        msg = "{:08x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
            id,bank,mod,dcf,dce,dcd,dcc,dcb,dca
        )        
        self.processandcheck(msg)
  
        id = 7
        bank = 0x1
        mod = 0x3f
        dcf = 12
        dce = 11
        dcd = 10
        dcc = 9
        dcb = 8
        dca = 7
        msg = "{:08x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
            id,bank,mod,dcf,dce,dcd,dcc,dcb,dca
        )        
        self.processandcheck(msg)

    def test_usbmsg9(self):
        id = 9
        enablemask = 0x555
        
        msg = "{:08x}{:04x}".format(
            id,enablemask
        )
        self.processandcheck(msg)

    def test_usbmsgb(self):
        id = 0xb
        digitalinputs = 0x555
        msg = "{:08x}{:04x}".format(
            id,digitalinputs
        )
        self.processandcheck(msg)

    def test_usbmsgd(self): #act curr
        
        id = 0xd
        mask = 0xf0f
        a12 = 12
        a11 = 11
        a10 = 10
        
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id,mask,a12,a11,a10
        )
        self.processandcheck(msg)

        id = 0x10d
        a9 = 9
        a4 = 4
        a3 = 3
        a2 = 2
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id,a9,a4,a3,a2
        )
        #self.processandcheck(msg)        

        id = 0x20d
        a1 = 1
        msg = "{:08x}{:04x}".format(
            id,a1
        )
        #self.processandcheck(msg)  

    def test_usbmsgf(self): #speed
        id = 0xf
        mask = 0xf
        f4 = 4
        f3 = 3
        f2 = 2
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id,mask,f4,f3,f2
        )
        self.processandcheck(msg)
        
        id = 0x10f
        f1 = 1
        msg = "{:08x}{:04x}".format(
            id,f1
        )
        self.processandcheck(msg)

    def test_usbmsg11(self): #adc
        id = 0x11
        mask = 0xff
        a8 = 8
        a7 = 7
        a6 = 6

        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id,mask,a8,a7,a6
        )     
        self.processandcheck(msg)

        id = 0x111
        a5 = 5
        a4 = 4
        a3 = 3
        a2 = 2
        msg = "{:08x}{:04x}{:04x}{:04x}{:04x}".format(
            id,a5,a4,a3,a2
        )     
        self.processandcheck(msg)
        id = 0x211
        a1 = 1
        msg = "{:08x}{:04x}".format(
            id,a1
        )     
        self.processandcheck(msg)

    def test_usbmsg13(self): #relay
        id = 0x13
        relays = 0x11
        msg = "{:08x}{:02x}".format(
            id,relays
        )
        self.processandcheck(msg)

    def test_usbmsg1d(self): #act fault
        id = 0x1d
        sync = 0
        faults = 0x555
        msg = "{:08x}{:01x}{:03x}".format(
            id,sync,faults
        )
        self.processandcheck(msg)

    def test_usbmsg41(self): #version
        id = 0x41
        hi = 0xb
        lo = 0xa
        patch = 0xd
        msg = "{:08x}{:04x}{:04x}{:04x}".format(
            id,hi,lo,patch
        )
        self.processandcheck(msg)
