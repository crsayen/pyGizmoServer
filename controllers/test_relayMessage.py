from controllers.testcube_usb_controller import RelayMessage
from controllers.testcube_usb_controller import PwmMessage

def test_init():
    rm = RelayMessage()
    assert(rm.get_relay_messages()==[])

def test_relay0on():
    rm = RelayMessage()
    rm.setRelay(0,True)
    assert(rm.get_relay_messages()==["000000120101"])

def test_relay1on0off():
    rm = RelayMessage()
    assert(rm.get_relay_messages()==[])
    rm.setRelay(0,False)
    assert(rm.get_relay_messages()==["000000120100"])
    rm.setRelay(1,True)
    assert(rm.get_relay_messages()==["000000120302"])

def test_pwmfreq():
    pm = PwmMessage()
    assert(pm.get_pwm_messages()==[])
    pm.setPwmFrequency(0,100)
    assert(pm.get_pwm_messages()==["000000044000000000640000"])    
    pm.setPwmFrequency(1,0x1234)
    assert(pm.get_pwm_messages()==["00000004c000000000641234"])

def test_pwmhiconf():
    pm = PwmMessage()
    pm.sethiconf(0,True)
    pm.sethiconf(8,False)
    assert(pm.get_pwm_messages()==["000000040101000100000000"])

def test_pwmduty():
    pm = PwmMessage()
    pm.setPwmDutyCycle(0,50)
    pm.setPwmDutyCycle(4,50)
    assert(pm.get_pwm_messages()==["000000060011320000003200"])   
    pm.setPwmDutyCycle(6,50)
    assert(pm.get_pwm_messages()==["000000060011320000003200","000000060101320000000000"])

def test_pwmenable():
    pm = PwmMessage()
    assert(pm.get_pwm_messages()==[])
    pm.setPwmEnabled(0,True)
    pm.setPwmEnabled(8,False)
    assert(pm.get_pwm_messages()==["0000000801010001"])
