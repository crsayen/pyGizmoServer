class Endpoint:
    def __init__(self):
        print("init")

    def start(self):
        print("start")

    def setRelay(self, msg):
        print(f"set relay: {msg}")