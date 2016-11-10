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
    failure_log = []

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
        "Sets the current test as passed, enables the PASS button and disables the FAIL button."
        self.breakout = True
        self.state = "passed"
        self.suite.form.enable_pass_button()
        self.suite.form.disable_fail_button()

    def set_failed(self):
        "Sets the current test as failed, enables the FAIL button and disables the PASS button."
        self.breakout = True
        self.state = "failed"
        self.suite.form.disable_pass_button()
        self.suite.form.enable_fail_button()

    def reset(self):
        "Resets the current test's status and failure log."
        self.breakout = True
        self.failure_log = []
        self.state = "not_run"

    def log_failure(self, text, print_to_screen = True):
        "Adds the specified text to the test's failure_log list and appends text to the form info label"
        self.failure_log.append(text)
        
        if print_to_screen:
            self.suite.form.append_text_line(text)

    def format_state(self):
        return {
            "passed": "Passed",
            "failed": "FAILED",
            "not_run": "Not Run"
        }.get(self.state, "Unknown")


class Test00_TestTest(TestProcedure):
    description = "00. Fake test"

    def run(self):
        self.suite.form.enable_test_buttons()
        self.suite.form.set_text("Pass or fail this test")

"""
The classes below are "live" tests run as part of the ATE itself. They are not unit tested.
"""

class Test0a_ConnectHardwareAndAwaitPowerOn(TestProcedure):

    description = "0a. Connect PCBA & cable set to test station"
    aborts = True

    def run(self):

        self.suite.form.disable_test_buttons()
        
        self.suite.form.set_text("Install PCB assemblies and apply PCBA power when ready.")

        ch1 = Channel(AD1_Pogo_Input_Volts)

        # Wait for channel 1 voltage

        while ch1.zero_voltage():
            time.sleep(0.1)
            self.suite.form.update()

            if self.breakout:
                return

        self.suite.form.append_text_line("Voltage received, awaiting +5v")

        got_5v = ch1.await_voltage(5.0, 0.01)

        # We have a voltage and it's 5v
        if got_5v:
            # Skip straight to the next test.
            self.suite.pass_test()

        # Not got 5v and/or timeout reached.
        else:
            self.set_failed()
            self.log_failure("Pogo input volts ({}) was outside of expected parameter (5.0v) or timeout reached".format(ch1.read_voltage()))


class Test1a_MeasurePowerOnDelay(TestProcedure):
    """AD1 volts applied, wait DIP1 high then count to DIP1 low"""

    description = "1a. Power on delay from pogo power to tablet power (400-600ms)"

    def run(self):

        # Disable test buttons here as we're waiting for digio input.
        self.suite.form.disable_test_buttons()

        self.suite.form.set_text("Waiting for DIP1 to become high")

        dip1_high = digio.await_high(DIP1_TP3_Q4_Startup_Delay)

        if not dip1_high:
            self.log_failure("DIP1 did not become high, cannot measure power on delay. Test failed.")
            self.set_failed()

        else:
            self.suite.form.append_text_line("Got high, waiting for DIP1 to go low")
            before = datetime.now()

            got_low = digio.await_low(DIP1_TP3_Q4_Startup_Delay)

            if got_low:
                after = datetime.now()
                span = (after - before)

                delay_ms = (span.microseconds / 1000)
                delay_ms = delay_ms + (span.seconds * 1000)
        
                self.suite.append_text("Detected delay of %ims" % delay_ms)
                self.suite.append_text("Tablet USB voltage is %d" % (Channel(AD2_Tablet_USB_Volts).read_voltage()))
                self.suite.append_text("External USB voltage is %d" % (Channel(AD6_External_USB_Volts).read_voltage()))

                if delay_ms >= 400 and delay_ms <= 600:
                    self.suite.append_text("Delay of %ims is within bounds (400ms to 600ms)" % delay_ms)
                else:
                    self.suite.append_text("WARNING: Delay of %ims is out of bounds (between 400ms and 600ms)" % delay_ms)

            else:
                self.suite.form.append_text_line("Awaiting DIP1 low timed out. Press RESET to try again.")
                self.suite.form.disable_pass_button()

class Test1b_PogoPowerInput(TestProcedure):
    """Pogo power input"""

    description = "1b. Pogo power input"

    def setUp(self):
        digio.set_high(DOP1_Tablet_Full_Load_Switch)

    def run(self):
        self.suite.form.set_text("Observe LED PCB D1 is RED")
        self.log_failure("User indicated LED PCB D1 is not illuminated", False)

class Test1c_ChargeBatteryStep1(TestProcedure):
    """Pogo power to battery board"""

    description = "1c. Charge Battery (Step 1)"

    def run(self):

        ad3 = Channel(AD3_Batt_Board_Power_In_Volts)
        valid, voltage = ad3.voltage_between(4.95, 5.05, 0.01)

        text = "Detected +{}v on battery board (AD3)."

        if not valid:
            text += "\n\nWARNING: This voltage is OUTSIDE of the required bounds (>= 4.95 and <= 5.05)"

        text += "\n\nConfirm LED D5 is illuminated RED"
        text += "\n\nConfirm LEDs D2 and D4 are OFF completely"
        text += "\nIf D2 or D4 have illuminated at all, fail the test"

        self.suite.form.set_text(text.format(voltage))
        self.log_failure("User indicated LED D5 is NOT illuminated red and/or D2 or D4 are illuminated")
        
class Test1c_ChargeBatteryStep2(TestProcedure):
    """Measure pogo power voltage divider"""

    description = "1c. Charge Battery (Step 2)"

    def run(self):
        self.suite.form.set_text("Reading voltage on AD4")
        ad4 = Channel(AD4_Batt_Board_Temp_Sense_Cutoff)

        if ad4.read_voltage() < 4.5:
            self.suite.form.append_text_line("Voltage is less than 4.5v")

            if ad4.voltage_between(2.0, 3.0, 0.01):
                self.suite.form.append_text_line("Voltage is between 2.0v and 3.0v")

                ad5 = Channel(AD5_Batt_Board_Battery_Volts)

                self.suite.form.append_text_line("Checking if AD5 voltage is between 3.0v and 4.07v")

                valid, volts = ad5.voltage_between(3.0, 4.07, 0.01)

                if valid:
                    if volts > 3.9:
                        self.suite.form.append_text_line("Voltage is above 3.9v, please change battery and reset test")
                    else:
                        self.suite.form.append_text_line("Battery PCB voltage is %.2f, test passed." % volts)
                        self.set_passed()

                else:
                    self.log_failure("Battery PCB voltage is %.2f, test failed." % volts)
                    self.set_failed()

        else:
            self.log_failure("Voltage is greater than 4.5v, test failed")
            self.set_failed()

class Test1d_TabletCharged(TestProcedure):
    """Check tablet charged"""

    description = "1d. Tablet Charged"

    def run(self):
        
        digio.set_low(DOP1_Tablet_Full_Load_Switch)
        digio.set_high(DOP2_Tablet_Charged_Load_Switch)

        self.suite.set_text("Observe LED D1 illuminated GREEN")
        self.log_failure("User indicated LED D1 was not illuminated green", False)
        

class Test2a_BatteryBoardPowersTabletStep1(TestProcedure):
    """Battery PCB and USB PCB Test"""

    description = "2a. Battery board powers tablet (Step 1)"

    def run(self):

        self.suite.form.set_text("Turn off Pogo Power (SW1) and turn on battery isolation switch (BATT-SW).\n\nPress PASS when completed.")
        self.suite.form.disable_fail_button()

class Test2a_BatteryBoardPowersTabletStep2(TestProcedure):

    description = "2a. Battery board powers tablet (Step 2)"

    def run(self):

        self.suite.form.set_text("Testing battery and USB PCBs")

        ad5 = Channel(AD5_Batt_Board_Battery_Volts)
        valid, volts = ad5.voltage_between(4.84, 4.88, 0.01)
        if valid:
            self.suite.form.append_text_line("Measured {}v on AD5 between bounds 4.84v and 4.88v, applying LOAD 2".format(volts))
            digio.set_high(DOP2_Tablet_Charged_Load_Switch)
            
            valid, volts = ad5.voltage_between(4.65, 4.85, 0.01)
            if valid:
                self.suite.form.append_text_line("Measured {}v on AD5, between bounds of 4.65v and 4.85v after LOAD 2 applied, test passed".format(volts))
                self.set_passed()
            else:
                self.log_failure("Measured {}v on AD5, OUT OF BOUNDS between 4.65v and 4.85v. Test failed".format(volts))
                self.set_failed()

        else:
            self.log_failure("Measured {}v on AD5, OUT OF BOUNDS between 4.84v and 4.88v. Test failed".format(volts))
            self.set_failed()

class Test2b_PogoPinsIsolatedFromBatteryPower(TestProcedure):

    description = "2b. Pogo Pins isolated from Battery Power"

    def run(self):
        self.suite.form.enable_test_buttons()
        self.suite.form.set_text("Reading voltage from AD1, expecting 0V")

        ad1 = Channel(AD1_Pogo_Input_Volts)

        if ad1.zero_voltage():
            self.suite.form.append_text_line("Zero voltage from AD1 received. Test passed")
            self.set_passed()
        else:
            self.log_failure("Got {}v from AD1, test failed".format(ad1.read_voltage()))
            self.set_failed()

class Test2c_LEDStatusNotInChargeState(TestProcedure):
    
    description = "2c. LED status (not in charge state)"

    def run(self):

        self.suite.form.set_text("Observe LED PCB (D1) is off.\n\nNo illumination = PASS. Green or red illumination = FAIL")
        self.log_failure("User indicated LED PCB (D1) is illuminated, should be off", False)


class Test2d_BattBoardPowerInputViaPogoDisconnected(TestProcedure):

    description = "2d. Battery Board power input via PoGo disconnected"

    def run(self):

        self.suite.form.set_text("Checking battery board power via PoGo is disconnected")
        ad2 = Channel(AD2_Tablet_USB_Volts)

        if ad2.zero_voltage():
            self.suite.form.append_text_line("Zero volts received on AD2. Test passed")
            self.set_passed()
        else:
            self.log_failure("Voltage detected on AD2, test failed.")
            self.set_failed()

class Test3a_ActivationOfOTGPower(TestProcedure):

    description = "3a. Activation of On The Go power"

    def run(self):

        self.suite.form.set_text("Test activation of On The Go (OTG) power")

        digio.set_low(DOP3_OTG_Mode_Trigger)

        otg_triggered = digio.await_low(DIP2_Tablet_OTG_Sense)

        if otg_triggered:
            self.suite.form.append_text_line("On the go power was triggered, test passed.")
            self.set_passed()
        else:
            self.log_failure("OTG power was not detected on DIP2, test failed")
            self.set_failed()

class Test3b_PogoPinsIsolatedFromOTGModePower(TestProcedure):

    description = "3b. Pogo pins isolated from tablet OTG mode power"

    def run(self):
        self.suite.form.set_text("Test pogo pins isolated from tablet OTG mode power")

        ad1 = Channel(AD1_Pogo_Input_Volts)

        if ad1.zero_voltage():
            self.suite.form.append_text_line("Zero voltage received on AD1, pogo pins are isolated. Test passed.")
            self.set_passed()
        else:
            self.log_failure("Voltage detected ({}v) on AD1, OTG mode enabled so pogo voltage is unexpected. Test failed.".format(ad1.read_voltage()))
            self.set_failed()

class Test3c_LEDStatusNotInChargeState(TestProcedure):

    description = "3c. LED status (not in charge state)"

    def run(self):
        self.suite.form.set_text("Observe LED PCB (D1) is off.\n\nNo illumination = PASS. Green or red illumination = FAIL")
        self.log_failure("User indicated LED PCB (D1) is illuminated, should be off", False)


class Test3d_BattBoardPowerInputViaPogoDisconnected(TestProcedure):

    description = "3d. Battery board power input via PoGo disconnected"

    def run(self):

        self.suite.form.set_text("Checking battery board input isolation")

        ad3 = Channel(AD3_Batt_Board_Power_In_Volts)

        if ad3.zero_voltage():
            self.suite.form.append_text_line("Got zero volts, battery isolated. Test passed.")
            self.set_passed()
        else:
            self.log_failure("Voltage detected ({}v) on AD3. Battery board power input should be disconnected. Test failed.")
            self.set_failed()

class Test3e_NoExternalBattVoltageToTabletStep1(TestProcedure):

    description = "3e. No external battery voltage presented to tablet +VE (Step 1)"

    def run(self):
        self.suite.form.enable_test_buttons()
        ad7 = Channel(AD7_Pogo_Battery_Output)

        valid, voltage = ad7.voltage_between(4.84, 4.88, 0.01)
        self.suite.form.set_text("Detected voltage: {}v on AD7".format(voltage))

        if valid:
            self.suite.form.append_text_line("Voltage is within bounds of 4.84v to 4.88v, passed.")
            self.suite.form.append_text_line("Toggle switch BATT-SW to isolate battery. PASS when completed.")
            self.set_passed()
        else:
            self.log_failure("Voltage was NOT within bounds of 4.84v to 4.88v, failed")
            self.set_failed()

class Test3e_NoExternalBattVoltageToTabletStep2(TestProcedure):

    description = "3e. No external battery voltage presented to tablet +VE (Step 2)"

    def run(self):
        ad7 = Channel(AD7_Pogo_Battery_Output)

        self.suite.form.enable_test_buttons()

        if ad7.zero_voltage():
            self.suite.form.append_text_line("Zero voltage detected on AD7, test passed")
            self.set_passed()
        else:
            self.suite.form.append_text_line("Voltage detected ({}v) on AD7, test failed. Check BATT-SW is toggled and press RESET.")
            self.suite.form.append_text_line("If BATT-SW is toggled, the test has failed.")
            self.set_failed()

class Test3f_USBCableContinuityTest(TestProcedure):

    description = "3f. USB cable continuity for data transfer"

    def run(self):

        self.suite.form.enable_test_buttons()
        self.suite.form.set_text("Measuring continuity on USB data lines")

        got_Dplus = False
        got_Dminus = False

        digio.set_high(DOP4_Dplus_Ext_USB)
        if digio.await_high(DIP3_Dplus_Tablet_USB_Sense, 3):
            digio.set_low(DOP4_Dplus_Ext_USB)
            if not digio.read(DIP3_Dplus_Tablet_USB_Sense):
                self.suite.form.append_text_line("D+ continuity OK")
                got_Dplus = True
            else:
                self.log_failure("D+ continuity (DOP4 -> DIP3): did not read return to low on DIP3")
        else:
            self.log_failure("D+ no signal")

        digio.set_low(DOP4_Dplus_Ext_USB)

        digio.set_high(DOP5_Dminus_Ext_USB)
        if digio.await_high(DIP4_Dminus_Tablet_USB_Sense, 3):
            digio.set_low(DOP5_Dminus_Ext_USB)
            if not digio.read(DIP4_Dminus_Tablet_USB_Sense):
                self.suite.form.append_text_line("D- continuity OK")
                got_Dminus = True
            else:
                self.log_failure("D- continuity (DOP5 -> DIP4): did not read return to low on DIP4")
        else:
            self.log_failure("D- no signal")

        digio.set_low(DOP5_Dminus_Ext_USB)

        if got_Dminus and got_Dplus:
            self.suite.form.append_text_line("Continuity for D+ and D- OK, test passed")
            self.set_passed()
        else:
            self.log_failure("Continuity error(s). Check data lines on USB and reset")
            self.set_failed()

class TestEnd_TestsCompleted(TestProcedure):
    
    description = "Testing completed"

    def run(self):
        self.suite.form.set_text("All tests finished. Press PASS to display the test summary")
        self.set_passed()