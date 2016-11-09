"Dummy module for using RPi.GPIO methods on Windows."

_pins = {}

# RPi.GPIO flags
BCM = 11
BOARD = 10
OUT = 0
IN = 1
HIGH = 1
LOW = 0

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