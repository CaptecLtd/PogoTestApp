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

# Specify which pins belong to which group
outputs = [
    DOP1_Load_ON,
    DOP2_Discharge_Load,
    DOP3_TP7_GPIO,
    DOP4_TP5_GPIO,
    DOP5_TP6_GPIO,
    DOP6_T_SW_ON,
    DOP7_Cold_sim,
    DOP8_Hot_sim,
    DOP9_TO_J7_1,
    DOP10_FLT_loop_back,
    DOP11_POGO_ON_GPIO,
    DOP12_BAT1_GPIO,
    DOP13_BAT0_GPIO
]

inputs = [
    DIP1_PWRUP_Delay,
    DIP2_OTG_OK,
    DIP3_Dplus_J5_3_OK,
    DIP4_Dminus_J5_2_OK,
    DIP5_5V_PWR,
    DIP6_From_J7_4,
    DIP7_J3_LINK_OK,
    DIP8_LED_RD,
    DIP9_LED_GN,
    DIP10_USB_PERpins_OK,
    DIP11_5V_ATE_in
]

def setup():
    "Set the GPIO pins to how we want them for the application"
    GPIO.setmode(GPIO.BCM)
    print("Pin Setup")
    # Configure input and output pins accordingly
    GPIO.setup(outputs, GPIO.OUT)
    GPIO.setup(inputs, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    # Set all the output pins low
    GPIO.output(outputs, GPIO.LOW)

    # Set DOP3 as input initially to represent a floating pin
    # This must be done AFTER all the output pins are configured, otherwise GPIO.output will throw an exception.
    #GPIO.setup(DOP3_TP7_GPIO, GPIO.IN)


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
        print(waiting)
        if read(pin):
            return True, waiting

        time.sleep(0.1)
        waiting += 0.1

    return False, waiting

def await_low(pin, timeout = 10):
    "Waits timeout seconds for pin to go low. Returns True if pin did become low, or False if timeout reached"

    waiting = 0
    timed_out = False
    while waiting <= timeout:

        if not read(pin):
            return True, waiting

        time.sleep(0.1)
        waiting += 0.1

    return False, waiting

def read_all_inputs():
    "Reads all the defined input pins and returns a dictionary of pin: value"

    def parse(reading):
        return reading
        #if reading:
        #    return "High"
        #else:
        #    return "Low"

    return {
        "DIP1": parse(read(DIP1_PWRUP_Delay)),
        "DIP2": parse(read(DIP2_OTG_OK)),
        "DIP3": parse(read(DIP3_Dplus_J5_3_OK)),
        "DIP4": parse(read(DIP4_Dminus_J5_2_OK)),
        "DIP5": parse(read(DIP5_5V_PWR)),
        "DIP6": parse(read(DIP6_From_J7_4)),
        "DIP7": parse(read(DIP7_J3_LINK_OK)),
        "DIP8": parse(read(DIP8_LED_RD)),
        "DIP9": parse(read(DIP9_LED_GN)),
        "DIP10": parse(read(DIP10_USB_PERpins_OK)),
        "DIP11": parse(read(DIP11_5V_ATE_in))
    }

def read_all_outputs():
    "Reads all the defined output pins and returns a dictionary of pin: state"

    def parse(reading):
        if reading:
            return "On"
        else:
            return "Off"

    return {
        "DOP1": parse(read(DOP1_Load_ON)),
        "DOP2": parse(read(DOP2_Discharge_Load)),
        "DOP3": parse(read(DOP3_TP7_GPIO)),
        "DOP4": parse(read(DOP4_TP5_GPIO)),
        "DOP5": parse(read(DOP5_TP6_GPIO)),
        "DOP6": parse(read(DOP6_T_SW_ON)),
        "DOP7": parse(read(DOP7_Cold_sim)),
        "DOP8": parse(read(DOP8_Hot_sim)),
        "DOP9": parse(read(DOP9_TO_J7_1)),
        "DOP10": parse(read(DOP10_FLT_loop_back)),
        "DOP11": parse(read(DOP11_POGO_ON_GPIO)),
        "DOP12": parse(read(DOP12_BAT1_GPIO)),
        "DOP13": parse(read(DOP13_BAT0_GPIO))
    }
