class Channel(object):
    "Represents an analogue channel on an analogue to digital converter"

    def __init__(self, channel):
        self.index = channel

    index = 1 # the number of the channel this instance reads from

    def read_voltage(self):
        return 999.0 # replace this with actual voltage reading code...

    def zero_voltage(self):
        "Returns True if zero voltage is read from the channel, or False for any other value"
        return self.read_voltage() == 0.0

    def voltage_between(self, lower, upper):
        "Reads voltage from the channel and returns bool (is between lower and upper) and voltage read"
        v = self.read_voltage()
        return v >= lower and v <= upper, v