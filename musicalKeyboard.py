import keyboard
import asyncio, json
import websockets
import aiohttp
import http.client

CURR_KEY = ''

notes = {
    "a": 220,
    "aSharp": 233,
    "b": 247,
    "c": 262,
    "cSharp": 277,
    "d": 294,
    "dSharp": 311,
    "e": 330,
    "f": 349,
    "fSharp": 370,
    "g": 392,
    "gSharp": 415
}

keys = {
    "a": notes['a'],
    "w": notes['aSharp'],
    "s": notes["b"],
    "d": notes["c"],
    "r": notes["cSharp"],
    "f": notes["d"],
    "t": notes["dSharp"],
    "g": notes["e"],
    "h": notes["f"],
    "u": notes["fSharp"],
    "j": notes["g"],
    "i": notes["gSharp"],
    "k": notes["a"] * 2,
    "o": notes["aSharp"] * 2,
    "l": notes["b"] * 2,
    ";": notes["c"] * 2,
    "[": notes["cSharp"] * 2,
    "'": notes["d"] * 2,
    "5": 5
}



def handlePress(e):
    global CURR_KEY
    if e.name == CURR_KEY:
        return
    CURR_KEY = e.name
    freq = keys.get(e.name)
    if freq is not None:
        setFreq(freq)

def handleRelease(e):
    global CURR_KEY
    if e.name == CURR_KEY:
        CURR_KEY = ''
        setFreq(0)

keyboard.on_press(handlePress)

for key in keys:
    keyboard.on_release_key(key, handleRelease)


client = http.client.HTTPConnection("localhost:36364")
headers = {"Content-type": "application/json"}
def setFreq(freq):
    try:
        client.request(
            "POST",
            "/",
            json.dumps({
                "path": "/pwmController/bankB/frequency",
                "value": freq
            }),
            headers
        )
        print(client.getresponse().read().decode())
    except:
        pass


while True:
    pass