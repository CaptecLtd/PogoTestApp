"Digital I/O abstraction module"

import time as time
import atexit
from ATE.const import *

# Attempt to load the Raspberry Pi's GPIO module.
# If this fails, we fall back to a dummy version which doesn't actually do anything.
# This is used for development purposes where the GPIO module isn't available.
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("GPIO libraries could not be loaded. NO HARDWARE INTERACTION WILL TAKE PLACE.")
    import RPiDummy.GPIODummy as GPIO

def setup():
    "Set the GPIO pins to how we want them for the application"
    GPIO.setmode(GPIO.BCM)
        
    # Specify which pins belong to which group
    outputs = [
        DOP1_Tablet_Full_Load_Switch,
        DOP2_Tablet_Charged_Load_Switch,
        DOP3_OTG_Mode_Trigger,
        DOP4_Dplus_Ext_USB,
        DOP5_Dminus_Ext_USB
    ]

    inputs = [
        DIP1_TP3_Q4_Startup_Delay,
        DIP2_Tablet_OTG_Sense,
        DIP3_Dplus_Tablet_USB_Sense,
        DIP4_Dminus_Tablet_USB_Sense,
        DIP5_Tablet_OTG_Vout_Activate
    ]

    # Configure input and output pins accordingly
    GPIO.setup(outputs, GPIO.OUT)
    GPIO.setup(inputs, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    # Set all the output pins low
    GPIO.output(outputs, GPIO.LOW)

    # Set DOP3 as input initially to represent a floating pin
    # This must be done AFTER all the output pins are configured, otherwise GPIO.output will throw an exception.
    GPIO.setup(DOP3_OTG_Mode_Trigger, GPIO.IN)


# Reset the state of the GPIO pins when our application exits.
@atexit.register
def cleanup():
    "Clean up any of the configuation we've done to the pins"
    GPIO.cleanup()

def set_input(pin, pull_up_down = GPIO.PUD_OFF):
    GPIO.setup(pin, GPIO.IN, pull_up_down)

def set_output(pin):
    GPIO.setup(pin, GPIO.OUT)

def set_high(pin):
    "Set the specified pin to high or on"
    GPIO.output(pin, GPIO.HIGH)

def set_low(pin):
    "Set the specified pin to low or off"
    GPIO.output(pin, GPIO.LOW)

def read(pin):
    "Returns True if the pin is high or False if the pin is low"
    return GPIO.input(pin)

def await_high(pin, timeout = 10):
    "Waits timeout seconds for pin to go high. Returns True if pin did go high, or False if timeout reached"
    waiting = 0
    timed_out = False
    while waiting <= timeout:

        if read(pin):
            return True

        time.sleep(0.1)
        waiting += 0.1

    return False

def await_low(pin, timeout = 10):
    "Waits timeout seconds for pin to go low. Returns True if pin did become low, or False if timeout reached"

    waiting = 0
    timed_out = False
    while waiting <= timeout:

        if not read(pin):
            return True

        time.sleep(0.1)
        waiting += 0.1

    return False

def read_all_inputs():
    "Reads all the defined input pins and returns a dictionary of pin: value"

    def parse(reading):
        if reading:
            return "High"
        else:
            return "Low"

    return {
        "DIP1": parse(read(DIP1_TP3_Q4_Startup_Delay)),
        "DIP2": parse(read(DIP2_Tablet_OTG_Sense)),
        "DIP3": parse(read(DIP3_Dplus_Tablet_USB_Sense)),
        "DIP4": parse(read(DIP4_Dminus_Tablet_USB_Sense)),
        "DIP5": parse(read(DIP5_Tablet_OTG_Vout_Activate))
    }

def read_all_outputs():
    "Reads all the defined output pins and returns a dictionary of pin: state"

    def parse(reading):
        if reading:
            return "On"
        else:
            return "Off"

    return {
        "DOP1": parse(read(DOP1_Tablet_Full_Load_Switch)),
        "DOP2": parse(read(DOP2_Tablet_Charged_Load_Switch)),
        "DOP3": parse(read(DOP3_OTG_Mode_Trigger)),
        "DOP4": parse(read(DOP4_Dplus_Ext_USB)),
        "DOP5": parse(read(DOP5_Dminus_Ext_USB))
    }