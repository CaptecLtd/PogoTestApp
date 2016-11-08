"Digital I/O abstraction module"

try:
    import RPi.GPIO as GPIO
    from ATE.const import *
    import time as time
except RuntimeError:
    print("GPIO libraries could not be loaded. NO HARDWARE INTERACTION WILL TAKE PLACE.")

def set_up():
    GPIO.setmode(GPIO.BCM)
        
    outputs = [
        DOP1_Tablet_Full_Load_Switch,
        DOP2_Tablet_Changed_Load_Switch,
        DOP3_OTG_Mode_Trigger
    ]

    inputs = [
        DIP1_TP3_Q4_Startup_Delay,
        DIP2_Tablet_OTG_Sense,
        DIP3_Dplus_Tablet_USB_Sense,
        DIP4_Dminus_Tablet_USB_Sense
    ]

    GPIO.setup(outputs, GPIO.OUT)
    GPIO.setup(inputs, GPIO.IN)

def cleanup():
    GPIO.cleanup()

def set_high(pin):
    GPIO.output(pin, True)

def set_low(pin):
    GPIO.output(pin, False)

def read(pin):
    return GPIO.input(pin)

def await_high(pin, timeout = 10):

    waiting = 0
    timed_out = False
    while not read(pin) and waiting <= timeout:
        time.sleep(0.1);
        waiting += 0.1

    