from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers

# Define a "singleton" for accessing the ADC Pi board
_i2c_helper = ABEHelpers()
_bus = _i2c_helper.get_smbus()
adc = ADCPi(bus, 0x68, 0x69, 18)

class Channel(object):
    "Represents an analogue channel on an analogue to digital converter"

    def __init__(self, channel):
        self.index = channel

    index = 1 # the number of the channel this instance reads from

    def read_voltage(self):
        try:
            return adc.read_voltage(self.index) # replace this with actual voltage reading code...
        except:
            return -1

    def zero_voltage(self):
        "Returns True if zero voltage is read from the channel, or False for any other value"
        return self.read_voltage() == 0.0

    def voltage_between(self, lower, upper):
        "Reads voltage from the channel and returns bool (is between lower and upper) and voltage read"
        v = self.read_voltage()
        return v >= lower and v <= upper, v