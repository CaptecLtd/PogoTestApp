import time
import random
from datetime import datetime, timedelta

from ATE.suite import TestSuite
from ATE.adc import Channel
import ATE.digio as digio
from ATE.const import *

class TestProcedure(object):
    "Base test class. All other tests should descend from this class."

    # When set to true, failing the test will abort the suite.
    aborts = False

    # When a test is passed, failed or reset, this variable becomes true. Use this to break out of infinite loops.
    breakout = False

    # A description of what the test is doing. This is shown on the GUI.
    description = None

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

class ConnectHardwareAndAwaitPowerOn(TestProcedure):
    description = "0a. Connect PCBA & cable set to test station"

    def run(self):

        self.suite.form.disable_test_buttons()
        self.suite.set_text("Install PCBA assembly and apply PCBA power when ready.")

        ch1 = Channel(AD1_Pogo_Input_Volts)

        # Wait for channel 1 voltage

        while ch1.zero_voltage():
            time.sleep(0.1)
            self.suite.form.update()

            if self.breakout:
                return

        got_5v = ch1.await_voltage(5.0, 0.01)

        self.suite.form.set_reading_value("AD1", ch1.read_voltage_range(10, sleep = 0.0))

        # We have a voltage and it's 5v(ish)
        if got_5v:
            self.suite.pass_test()
        else:
            self.suite.form.set_text("Pogo input volts was outside of expected parameter (5.0v)")
            self.suite.fail_test()

class MeasurePowerOnDelay(TestProcedure):
    """Pogo power on delay"""

    description = "1a. Power on delay from pogo power to tablet power (400-600ms)"

    def run(self):

        digio.await_high(DIP1_TP3_Q4_Startup_Delay)

        before = datetime.now()

        # timeout after 10 seconds and fail the test
        timeout = 10
        loops = 0

        while loops <= timeout:
        
            # Check to see if we've gone low. If we have, break out of loop.
            if digio.await_low(DIP1_TP3_Q4_Startup_Delay):
                break

            time.sleep(0.1)
            self.suite.form.update()
            loops += 1

            if self.breakout:
                return
          
        after = datetime.now()
        delay_ms = (after - before)
        
        self.suite.append_text("Detected delay of %ims" % delay_ms)
        self.suite.append_text("Channel 2 voltage is %d" % ch2.read_voltage())

        if delay_ms >= 400 and delay_ms <= 600:
            self.suite.pass_test()
        else:
            self.suite.append_text("WARNING: Delay {} is out of bounds (between 400ms and 600ms)".format(delay_ms))

class PogoPowerInput(TestProcedure):
    """Pogo power input"""

    description = "1b. Pogo power input"

    def setUp(self):
        digio.set_high(DOP1_Tablet_Full_Load_Switch)

    def run(self):
        self.suite.form.enable_test_buttons()
        self.suite.form.set_text("Observe LED PCB D1 is RED")

class ChargeBatteryStep1(TestProcedure):
    """Pogo power to battery board"""

    description = "1c. Charge Battery (Part 1)"

    def run(self):

        ch3 = Channel(AD3_Batt_Board_Power_In_Volts)
        valid, voltage = ch3.voltage_between(4.95, 5.05)

        text = "Detected +{}V on battery board."
        text += "\n\nConfirm LED D5 is illuminated RED"
        text += "\nConfirm LEDs D2 and D4 are OFF completely"
        text += "\n\nIf D2 or D4 have illuminated at all, fail the test"

        self.suite.set_text(text.format(voltage))
        
class ChargeBatteryStep2(TestProcedure):
    """Measure pogo power voltage divider"""

    description = "1c. Charge Battery (Part 2)"

    def run(self):
        self.suite.set_text("Reading voltage on AD4")
        ch4 = Channel(AD4_Batt_Board_Temp_Sense_Cutoff)

        if ch4.read_voltage() < 4.5:
            self.suite.append_text("Voltage is less than 4.5v")

            if ch4.voltage_between(2.0, 3.0, 0.01):
                self.suite.append_text("Voltage is between 2.0v and 3.0v")

                ch5 = Channel(AD5_Batt_Board_Battery_Volts)

                self.suite.append_text("Checking if AD5 voltage is between 3.0v and 4.07v")

                if ch5.voltage_between(3.0, 4.07, 0.01):
                    v = ch5.read_voltage()

                    if v > 3.9:
                        self.suite.append_text("Voltage is above 3.9v, please change battery and restart test")
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

    description = "1d. Tablet Charged"

    def run(self):
        
        digio.set_low(DOP1_Tablet_Full_Load_Switch)
        digio.set_high(DOP2_Tablet_Charged_Load_Switch)

        self.suite.set_text("Observe LED D1 illuminated GREEN")
        

class BatteryBoardPowersTablet(TestProcedure):
    """Battery PCB and USB PCB Test"""

    description = "2a. Battery board powers tablet"

    def run(self):
        self.suite.form.set_text("Turn off Pogo Power (SW1) and turn on battery isolation switch (BATT-SW)")


