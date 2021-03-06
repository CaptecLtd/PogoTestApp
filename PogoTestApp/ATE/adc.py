# Import our required modules and methods
from time import sleep
from ATE import const

# Try loading the ADC modules. If not, enable simulation mode.
# Simulation mode doesn't read any values from the ADC, instead it just returns the value of whatever is set by Channel.set_simulation_voltage()
# This is principally used for development on Windows (where there is no GPIO or ADC) and for running unit tests on these functions.
simulation_mode = False
try:
    from ADCPi.ABE_ADCPi import ADCPi
    from ADCPi.ABE_helpers import ABEHelpers
except:
    print("ADC libraries could not be loaded, simulation mode enabled. VOLTAGES WILL NOT BE READ FROM HARDWARE!")
    simulation_mode = True

if not simulation_mode:
    _i2c_helper = ABEHelpers()
    _bus = _i2c_helper.get_smbus()
    adc = ADCPi(_bus, 0x68, 0x69, 12)

def read_all_voltages():
    "Reads the voltages from all defined analogue channels"
    def read(channel):
        return round(Channel(channel).read_voltage(), 2)

    return {
        "AD1": read(const.AD1_V_pogo),
        "AD2": read(const.AD2_V_5V_pwr),
        "AD3": read(const.AD3_V_in),
        "AD4": read(const.AD4_V_TP13_NTC),
        "AD5": read(const.AD5_V_bat),
        "AD6": read(const.AD6_V_sense),
        "AD7": read(const.AD7_V_sys_out),
        "AD8": read(const.AD8_V_out)
    }

def get_all_channels():
    "Returns a dictionary of all channels"

    return {
        "AD1": Channel(const.AD1_V_pogo),
        "AD2": Channel(const.AD2_V_5V_pwr),
        "AD3": Channel(const.AD3_V_in),
        "AD4": Channel(const.AD4_V_TP13_NTC),
        "AD5": Channel(const.AD5_V_bat),
        "AD6": Channel(const.AD6_V_sense),
        "AD7": Channel(const.AD7_V_sys_out),
        "AD8": Channel(const.AD8_V_out)
    }

# Contains a dictionary of channel: factor values.
# If a channel is loaded matching the key, all readings will be multiplied by factor.
conversion_factors = {}

# The overall conversion factor for all channels if not defined in the conversion_factors list
global_conversion_factor = 1.0

class Channel(object):
    "Represents an analogue channel on an analogue to digital converter"

    index = None # the number of the channel this instance reads from

    # Simulation variables used for testing when ADC is not available.
    _simulation_mode = False
    _simulation_voltage = 0.0
    
    # Value to adjust the voltage read by on this channel.
    _conversion_factor = 1.0

    def __init__(self, channel, conversion_factor = 1.0):
        self.index = channel

        # If there is a global conversion factor set other than the default 1.0
        if global_conversion_factor != 1.0:
            self._conversion_factor = global_conversion_factor

        # If the conversion factor is left as default
        if conversion_factor == 1.0:
            
            # Look it up in our global conversion factors dictionary
            if self.index in conversion_factors.keys():
                # And apply it
                self._conversion_factor = conversion_factors[self.index]

        # Otherwise if it is set on the class constructor
        else:
            # Set it as requested.
            self._conversion_factor = conversion_factor

        if simulation_mode:
            self.set_simulation_mode(True)

    def set_simulation_mode(self, enable):
        "Defines whether this class instance actually reads from the channel or just returns voltage provided by set_simulation_voltage()"
        self._simulation_mode = enable

    def set_simulation_voltage(self, value):
        "Sets the voltage which will be returned by read_voltage() if the class instance is in simulation mode"
        self._simulation_voltage = value

    def set_conversion_factor(self, factor):
        "Sets the conversion factor for this channel. The factor is added to whichever readings are returned from the ADC"
        self._conversion_factor = factor

    def read_voltage(self, decimal_places = 4):
        "Reads a single voltage value from the A/D converter or the _simulation_voltage var if in simulation mode"
        if self._simulation_mode:
            return self._simulation_voltage
        else:
            return round(adc.read_voltage(self.index) * self._conversion_factor, decimal_places)

    def read_voltage_range(self, sample_size = 1, tolerance = 0.01, sleep = 0.1):
        "Reads voltage sample_size times with a sleep seconds delay and returns (voltage, True, readings) if all readings are within tolerance, or (voltage, False, readings) if a reading is not in tolerance"
        loop = 0
        readings = []
        valid = True

        while loop < sample_size:
            readings.append(self.read_voltage())
            loop += 1
           
        for reading in readings:
            for iteration in range(0, sample_size):
                if not self.isclose(readings[iteration], reading, tolerance):
                    valid = False
                    break

        return float(sum(readings)) / max(len(readings), 1), valid, readings
        
    def zero_voltage(self):
        "Returns True if less than 1 volt is read from the channel, or False for any other value."
        return self.read_voltage() < 1.0

    def voltage_between(self, lower, upper, tolerance):
        "Reads voltage from the channel and returns bool (is between lower and upper) and voltage read"
        v = self.read_voltage()
        return ((self.isclose(lower, v, tolerance) or v >= lower) and (self.isclose(upper, v, tolerance) or v <= upper)), v

    def voltage_near(self, target, relative_tolerance, absolute_tolerance = 0.0):
        "Reads voltage from the channel and returns true if target is within tolerance, false if not"
        return self.isclose(target, self.read_voltage(), relative_tolerance, absolute_tolerance)

    def await_voltage(self, target, tolerance, timeout = 10):
        "Waits for the specified voltage within tolerance, returning true if matched or false if timeout seconds pass"
        time = 0
        while time <= timeout:
            if self.voltage_near(target, tolerance):
                return True
            else:
                sleep(0.5)
                time += 0.5

        return False
 
    # https://docs.python.org/3/library/math.html#math.isclose (in case we're not running Python 3.5)
    def isclose(self, expected, actual, relative_tolerance = 1e-09, absolute_tolerance = 0.0):
        return abs(expected-actual) <= max(relative_tolerance * max(abs(expected), abs(actual)), absolute_tolerance)           
