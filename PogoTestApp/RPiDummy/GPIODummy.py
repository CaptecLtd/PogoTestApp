"Dummy module for using RPi.GPIO methods on Windows."

_pins = {}

# RPi.GPIO flags
BCM = 11
BOARD = 10
OUT = 0
IN = 1
HIGH = 1
LOW = 0

# Set up 40 fake GPIO pins
for pin in range(1, 40):
    _pins[pin] = {}
    _pins[pin]["level"] = LOW
    _pins[pin]["mode"] = OUT

def setmode(mode):
    pass

def setup(pin, mode):

    def set(pin):
        _pins[pin]["mode"] = mode

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