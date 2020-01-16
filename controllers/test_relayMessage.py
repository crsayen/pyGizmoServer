from controllers.testcube_usb_controller import RelayMessage

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