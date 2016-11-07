from time import sleep

# Try loading the ADC modules. If not, enable simulation mode.
simulation_mode = False

try:
    from ADCPi.ABE_ADCPi import ADCPi
    from ADCPi.ABE_helpers import ABEHelpers
except:
    print("ADC libraries could not be loaded, simulation mode enabled. VOLTAGES WILL NOT BE READ FROM HARDWARE!")
    simulation_mode = True

if not simulation_mode:
    # Define a "singleton" for accessing the ADC Pi board
    _i2c_helper = ABEHelpers()
    _bus = _i2c_helper.get_smbus()
    adc = ADCPi(_bus, 0x68, 0x69, 18)

class Channel(object):
    "Represents an analogue channel on an analogue to digital converter"

    def __init__(self, channel, conversion_factor = 0.0):
        self.index = channel
        self._conversion_factor = conversion_factor

        if simulation_mode:
            self.set_simulation_mode(True)

    index = 1 # the number of the channel this instance reads from

    # Simulation variables used for testing when ADC is not available.
    _simulation_mode = False
    _simulation_voltage = 0.0
    
    # Value to adjust the voltage read by on this channel.
    _conversion_factor = 0.0

    def set_simulation_mode(self, enable):
        "Defines whether this class instance actually reads from the channel or just returns voltage provided by set_simulation_voltage()"
        self._simulation_mode = enable

    def set_simulation_voltage(self, value):
        "Sets the voltage which will be returned by read_voltage() if the class instance is in simulation mode"
        self._simulation_voltage = value

    def read_voltage(self):
        "Reads a single voltage value from the A/D converter or the _simulation_voltage var if in simulation mode"
        if self._simulation_mode:
            return self._simulation_voltage
        else:
            try:
                return adc.read_voltage(self.index) + self._conversion_factor
            except:
                return False

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
        "Returns True if zero voltage is read from the channel, or False for any other value"
        return self.voltage_near(0.0, 0.01)

    def voltage_between(self, lower, upper, tolerance):
        "Reads voltage from the channel and returns bool (is between lower and upper) and voltage read"
        v = self.read_voltage()
        return (self.isclose(lower, v, tolerance) or v >= lower) and (self.isclose(upper, v, tolerance) or v <= upper)

    def voltage_near(self, target, tolerance):
        "Reads voltage from the channel and returns true if target is within tolerance, false if not"
        return self.isclose(target, self.read_voltage(), tolerance)

    def await_voltage(self, target, tolerance, timeout = 10):
        "Waits for the specified voltage within tolerance, returning true if matched or false if timeout seconds pass"
        time = 0
        while time <= timeout:
            if self.voltage_near( target, tolerance):
                return True
            else:
                sleep(0.5)
                time += 0.5

        return False
 
    # https://docs.python.org/3/library/math.html#math.isclose (in case we're not running Python 3.5)
    def isclose(self, expected, actual, relative_tolerance = 1e-09, absolute_tolerance = 0.0):
        return abs(expected-actual) <= max(relative_tolerance * max(abs(expected), abs(actual)), absolute_tolerance)           
