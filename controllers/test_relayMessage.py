from controllers.testcube_usb_controller import RelayMessage
from controllers.testcube_usb_controller import PwmMessage

def test_init():
    rm = RelayMessage()
    assert(rm.get_message_string()=="000000120000")

def test_relay0on():
    rm = RelayMessage()
    rm.setstate(0,True)
    assert(rm.get_message_string()=="000000120101")

def test_relay1on0off():
    rm = RelayMessage()
    assert(rm.get_message_string()=="000000120000")
    rm.setstate(0,False)
    assert(rm.get_message_string()=="000000120100")
    rm.setstate(1,True)
    assert(rm.get_message_string()=="000000120302")

def test_pwmfreq():
    pm = PwmMessage()
    assert(pm.get_message_string()=="000000040000000000000000")
    pm.setfreq(0,100)
    assert(pm.get_message_string()=="000000044000000000640000")    
    pm.setfreq(1,0x1234)
    assert(pm.get_message_string()=="00000004c000000000641234")

    pm = PwmMessage()
    pm.sethiconf(0,True)
    pm.sethiconf(8,False)
    assert(pm.get_message_string()=="000000040101000100000000")

    