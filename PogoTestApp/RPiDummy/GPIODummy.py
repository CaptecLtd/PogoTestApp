"Dummy module for using RPi.GPIO methods on Windows."
print("GPIO dummy library loaded. No hardware interaction will take place.")

_pins = {}
_links = []

# RPi.GPIO flags
BCM = 11
BOARD = 10
OUT = 0
IN = 1
HIGH = 1
LOW = 0
PUD_DOWN = 21
PUD_UP = 22
PUD_OFF = 20
UNKNOWN = -1

# Set up 40 fake GPIO pins
for pin in range(1, 40):
    _pins[pin] = {}
    _pins[pin]["level"] = LOW
    _pins[pin]["mode"] = -1
    _pins[pin]["pud"] = PUD_OFF

def _short(pin1, pin2):
    _links.append((pin1, pin2))

def setmode(mode):
    pass

def setup(pin, mode, pull_up_down = PUD_OFF, initial = UNKNOWN):

    def set(pin):
        _pins[pin]["mode"] = mode
        _pins[pin]["level"] = initial
        _pins[pin]["pud"] = pull_up_down

    if type(pin).__name__ == "list":
        for p in pin:
            set(p)
    else:
        set(pin)

def cleanup():
    _pins = {}

def output(pin, level):

    def set(pin, level):
        _pins[pin]["level"] = level

    if type(pin).__name__ == "list":
        for p in pin:
            set(p, level)
    else:
        set(pin, level)

def input(pin):
    # If the pins is an input pin, check to see if it's "shorted" to an output pin
    if _pins[pin]["mode"] == IN:

        # Loop through the links. If any linked pin is an output pin, return it's output
        for k, link in enumerate(_links):
            pin1 = link[0]
            pin2 = link[1]
            if pin1 == pin and _pins[pin2]["mode"] == OUT:
                return _pins[pin2]["level"]
            if pin2 == pin and _pins[pin1]["mode"] == OUT:
                return _pins[pin1]["level"]

        # If there's no shorts, it's LOW.
        return LOW

    # Otherwise if the pin is an output pin, return what it's doing.
    elif _pins[pin]["mode"] == OUT:
        return _pins[pin]["level"]