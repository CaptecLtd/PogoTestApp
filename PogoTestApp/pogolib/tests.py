import time
import random

from suite import TestSuite
from adc import Channel

class TestProcedure(object):
    "Base test class. All other tests should descend from this class."

    # When set to true, failing the test will abort the suite.
    aborts = False

    suite = TestSuite()
    state = "not_run"

    def run(self):
        pass

    def set_passed(self):
        self.state = "passed"

    def set_failed(self):
        self.state = "failed"

    def reset(self):
        self.state = "not_run"

class MeasurePowerOnDelay(TestProcedure):
    """Pogo power on delay"""

    def run(self):
        self.suite.form.disable_test_buttons()
        self.suite.set_text("Please turn on LOAD 1. (this sample just simulates the switch being flipped)")

        ch1 = Channel(1)
        ch2 = Channel(2)

        # Wait for channel 1 voltage
        while ch1.zero_voltage():
            time.sleep(0.1)
            self.suite.form.update()

        self.suite.set_text("Got channel 1 load, measuring tablet power delay")
        
        # wait for channel 2 voltage
        delay = 0
        while ch2.zero_voltage():
            time.sleep(0.001)
            self.suite.form.update()
            delay +=1
        
        self.suite.append_text("Detected delay of %ims" % delay)
        self.suite.append_text("Channel 2 voltage is %d" % ch2.read_voltage())

        self.suite.form.enable_test_buttons()

class PogoPowerInput(TestProcedure):
    """Pogo power input"""

    aborts = True

    def run(self):
        text = "Check D1 LED on the LED PCB"
        text += "\n\nPASS = LED lit RED"
        text += "\nFAIL = LED is not lit"
        self.suite.set_text(text)
        
class ChargeBatteryStep1(TestProcedure):
    """Pogo power to battery board"""

    def run(self):
        # conditional to see whether TP5 and TP1 reads +5V (+/- 0.05V)

        ch1 = Channel(1)
        valid, voltage = ch1.voltage_between(4.95, 5.05)

        text = "Detected +{}V on battery board."
        text += "\n\nConfirm LED D5 is illuminated RED"
        text += "\nConfirm LEDs D2 and D4 are OFF completely"
        text += "\n\nIf D2 or D4 are illuminated at all, fail the test"

        self.suite.set_text(text.format(voltage))
        
class ChargeBatteryStep2(TestProcedure):
    """Measure pogo power voltage divider"""

    def run(self):
        # Conditional to measure TP1 and TP13 is below 4.5V
        self.suite.set_text("Measured 2.0V on voltage divider (TP1 and TP13\nMeasured 3.04V on battery PCB")

class TabletCharged(TestProcedure):
    """Check tablet charged"""

    def run(self):
        self.suite.form.msgbox("Action", "Turn off LOAD 1")
        self.suite.set_text("Observe LED D1 illuminated GREEN")
        

class BatteryBoardPowersTablet(TestProcedure):
    """Battery PCB and USB PCB Test"""

    def run(self):
        # Measure USB power between 
        pass

class FailTest(TestProcedure):
    """This test will automatically fail after 5 seconds"""

    def run(self):
        self.suite.set_text("This test will fail after 5 seconds")

        self.suite.form.update()
        time.sleep(5)

        self.suite.fail_test()