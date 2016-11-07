import time
import random
from datetime import datetime, timedelta

from ATE.suite import TestSuite
from ATE.adc import Channel
from ATE.const import *

class TestProcedure(object):
    "Base test class. All other tests should descend from this class."

    # When set to true, failing the test will abort the suite.
    aborts = False

    # When a test is passed, failed or reset, this variable becomes true. Use this to break out of infinite loops.
    breakout = False

    suite = TestSuite()
    state = "not_run"

    def setUp(self):
        "This method is called before run(). Tasks to be completed before the test itself begins should go here."
        pass

    def run(self):
        "The method which runs the actual test procedure"
        pass

    def tearDown(self):
        "This method is called after run() completes. Tasks to be completed after the test has finished should go here."
        pass

    def set_passed(self):
        self.breakout = True
        self.state = "passed"

    def set_failed(self):
        self.breakout = True
        self.state = "failed"

    def reset(self):
        self.breakout = True
        self.state = "not_run"

    def format_state(self):
        return {
            "passed": "Passed",
            "failed": "FAILED",
            "not_run": "Not Run"
        }.get(self.state, "Unknown")


"""
The classes below are "live" tests run as part of the ATE itself. They are not unit tested.
"""

class InstallHardware(TestProcedure):
    "Hardware installed to tester"

    aborts = True

    def run(self):
        self.suite.form.enable_test_buttons()
        self.suite.set_text("Turn off all loads before starting.\n\nPlease install all hardware according to instructions and press PASS when ready to begin.")

class MeasurePowerOnDelay(TestProcedure):
    """Pogo power on delay"""

    def run(self):
        self.suite.form.disable_test_buttons()
        self.suite.set_text("Please apply power to Pogo PCB J2.")

        ch1 = Channel(AD1_Pogo_Input_Volts)
        ch2 = Channel(AD2_Tablet_USB_Volts)

        # Wait for channel 1 voltage

        while ch1.zero_voltage():
            time.sleep(0.1)
            self.suite.form.update()

            if self.breakout:
                return

        self.suite.set_text("Got channel 1 load, measuring tablet power delay")
        
        # wait for channel 2 voltage
        before = datetime.now()

        # timeout after 10 seconds and fail the test
        timeout = 10000
        loops = 0

        while ch2.zero_voltage():
            time.sleep(0.1)
            self.suite.form.update()
            loops += 1

            if self.breakout:
                return
          
        after = datetime.now()
        delay_ms = (after - before)
        
        self.suite.append_text("Detected delay of %ims" % delay_ms)
        self.suite.append_text("Channel 2 voltage is %d" % ch2.read_voltage())
        self.suite.append_text("")

        if delay_ms >= 400 and delay_ms <= 600:
            self.suite.append_text("Delay is between 400ms and 600ms, PASS.")
        else:
            self.suite.append_text("WARNING: Delay is out of bounds (between 400ms and 600ms)")

        self.suite.form.enable_test_buttons()

class PogoPowerInput(TestProcedure):
    """Pogo power input"""

    aborts = True

    def run(self):

        self.suite.set_text("Enable LOAD 1 (1.8A). Test will fail if not enabled in 30 seconds.")
        self.suite.form.update()

        ch4 = Channel(4)
        if not ch4.await_voltage(5.0, 0.001, 30):
            self.suite.fail_test()

        self.suite.set_text("LOAD 1 received. Observe LED PCB ""D1"" is red")

        
        
        
class ChargeBatteryStep1(TestProcedure):
    """Pogo power to battery board"""

    def run(self):
        # conditional to see whether TP5 and TP1 reads +5V (+/- 0.05V)

        ch1 = Channel(1)
        valid, voltage = ch1.voltage_between(4.95, 5.05)

        text = "Detected +{}V on battery board."
        text += "\n\nConfirm LED D5 is illuminated RED"
        text += "\nConfirm LEDs D2 and D4 are OFF completely"
        text += "\n\nIf D2 or D4 have illuminated at all, fail the test"

        self.suite.set_text(text.format(voltage))
        
class ChargeBatteryStep2(TestProcedure):
    """Measure pogo power voltage divider"""

    def run(self):
        self.suite.set_text("Reading voltage on channel 2")
        ch2 = Channel(2)

        if ch2.read_voltage() < 4.5:
            self.suite.append_text("Voltage is less than 4.5v")

            if ch2.voltage_between(2.0, 3.0, 0.01):
                self.suite.append_text("Voltage is between 2.0v and 3.0v")

                ch3 = Channel(3)

                self.suite.append_text("Checking if channel 3 voltage is between 3.0v and 4.07v")

                if ch3.voltage_between(3.0, 4.07, 0.01):
                    v = ch3.read_voltage()

                    if v > 3.9:
                        self.suite.append_text("Voltage is above 3.9v, please change battery")
                    else:
                        self.suite.append_text("Battery PCB voltage is %20f, test passed." % ch3.read_voltage())

                else:
                    self.suite.append_text("Battery PCB voltage is %20f, test FAILED." % ch3.read_voltage())
                    self.suite.form.disable_pass_button()

        else:
            self.suite.append_text("Voltage is greater than 4.5v, test failed")
            self.suite.form.disable_pass_button()

    def tearDown(self):
        self.suite.form.enable_test_buttons()

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