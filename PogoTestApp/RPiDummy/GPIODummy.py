"Dummy module for using RPi.GPIO methods on Windows."

_pins = {}

BCM = 0
BOARD = 1
OUT = 2
IN = 3
HIGH = 4
LOW = 5

def setmode(mode):
    pass

def setup(pin, mode):

    def set(pin):
        if pin in _pins.items():
            _pins[pin]["mode"] = mode
        else:
            _pins[pin] = {}
            _pins[pin]["mode"] = mode
            _pins[pin]["level"] = 0

    if type(pin).__name__ == "list":
        for p in pin:
            set(p)
    else:
        set(pin)



def cleanup():
    _pins = {}

def output(pin, level):
    _pins[pin]["level"] = level

def input(pin):
    return _pins[pin]["level"]