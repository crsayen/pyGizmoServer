from pubsub import pub
import time, threading

class MockUSB:
    def __init__(self):
        threading.Thread(target=self.send_updates,args=([])).start()
        self.relays = [False, False, False, False, False, False]

    def start(self):
        pass

    def setRelay(self, relay, state):
        self.relays[relay] = state

    def xmit(self):
        data = [{"enabled": x} for x in self.relays]
        message = {"path":f"/relayController/relays/","data":data}
        pub.sendMessage("received_update",message=message)

    def send_updates(self):
        n = 0
        time.sleep(3)
        for i in range(10001):
            message = {}
            message["path"] = f"/adcController/adcs/",
            message["data"] = [{"measuredVoltage":x}for x in range(n,10+n)]
            pub.sendMessage("received_update", message=message)
            n+=1