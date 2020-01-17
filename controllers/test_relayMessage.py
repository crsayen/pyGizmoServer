from controllers.testcube_usb_controller import RelayMessage
from controllers.testcube_usb_controller import PwmMessage

def test_init():
    rm = RelayMessage()
    assert(rm.get_message_string()==None)

def test_relay0on():
    rm = RelayMessage()
    rm.setstate(0,True)
    assert(rm.get_message_string()=="000000120101")

def test_relay1on0off():
    rm = RelayMessage()
    assert(rm.get_message_string()==None)
    rm.setstate(0,False)
    assert(rm.get_message_string()=="000000120100")
    rm.setstate(1,True)
    assert(rm.get_message_string()=="000000120302")

def test_pwmfreq():
    pm = PwmMessage()
    assert(pm.get_message_string()==None)
    pm.setfreq(0,100)
    assert(pm.get_message_string()=="000000044000000000640000")    
    pm.setfreq(1,0x1234)
    assert(pm.get_message_string()=="00000004c000000000641234")

def test_pwmhiconf():
    pm = PwmMessage()
    pm.sethiconf(0,True)
    pm.sethiconf(8,False)
    assert(pm.get_message_string()=="000000040101000100000000")

def test_pwmduty():
    pm = PwmMessage()
    pm.setduty(0,50)
    pm.setduty(4,50)
    assert(pm.getUsbMsg6(0)=="000000060011320000003200")   
    assert(pm.getUsbMsg6(1)==None)
    pm.setduty(6,50)
    assert(pm.getUsbMsg6(1)=="000000060101320000000000")

def test_pwmenable():
    pm = PwmMessage()
    assert(pm.getUsbMsg8()==None)
    pm.setenabled(0,True)
    pm.setenabled(8,False)
    assert(pm.getUsbMsg8()=="0000000801010001")
