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

    # If the test is set as passed during execution and auto_advance is true, the
    # suite will advance to the next test automatically.
    auto_advance = False

    # If set to True, the pass/fail buttons will be enabled at the beginning of the test after a delay.
    # If set to False, the pass/fail buttons will be disabled. The test will need to enable them during execution.
    enable_pass_fail = True

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

        if self.suite.form:
            self.suite.form.enable_pass_button()
            self.suite.form.disable_fail_button()

    def set_failed(self):
        "Sets the current test as failed, enables the FAIL button and disables the PASS button."
        self.breakout = True
        self.state = "failed"

        if self.suite.form:
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


class TestXX_FakeTest(TestProcedure):

    description = "Fake test"

    def run(self):

        self.suite.form.set_text("Pass or fail")
        self.suite.form.append_image("Resources/Untitled.gif")
        self.suite.form.append_text_line("Middle text between gifs")
        self.suite.form.append_image("Resources/Untitled.gif")
        self.suite.form.append_text_line("Text after")

        #self.set_passed()

"""
The classes below are "live" tests run as part of the ATE itself. They are not unit tested.
"""

class Test0a_ConnectHardwareAndAwaitPowerOn(TestProcedure):

    description = "0a. Connect PCBA & cable set to test station"
    aborts = True
    auto_advance = True

    def run(self):

        self.suite.form.disable_test_buttons()
        str = """1. Install PCB Assemblies into jigs.
2. Connect POGO PCB to battery PCB. Turn on BATT-SW to connected state.
3. Connect POGO PCB USB lead to ATE.
4. Do NOT connect black ATE USB flylead to POGO PCB.
5. Turn battery switch (SW5) ON.
6. Turn POGO power (SW1) ON, only after SW5 is on.
"""
        self.suite.form.set_text(str)

        ad1 = Channel(AD1_Pogo_Input_Volts)

        # Wait for channel 1 voltage

        while ad1.zero_voltage():
            time.sleep(0.1)
            self.suite.form.update()

            if self.breakout:
                return

        self.suite.form.append_text_line("Voltage received, awaiting +5v")

        got_5v = ad1.await_voltage(5.0, 0.1, 2)

        # We have a voltage and it's 5v
        if got_5v:
            # Skip straight to the next test.
            self.set_passed()

        # Not got 5v and/or timeout reached.
        else:
            self.set_failed()
            self.log_failure("Pogo input volts ({}) was outside of expected parameter (5.0v) or timeout reached".format(ad1.read_voltage()))


class Test1a_MeasurePowerOnDelay(TestProcedure):
    """AD1 volts applied, wait DIP1 high then count to DIP1 low"""

    description = "1a. Power on delay from pogo power to tablet power"
    auto_advance = True

    def run(self):

        # Delays in milliseconds for Q4.
        delay_lower = 400
        delay_higher = 750

        # Disable test buttons here as we're waiting for digio input.
        self.suite.form.disable_test_buttons()

        self.suite.form.set_text("Waiting for DIP1 to become high")

        dip1_high = digio.await_high(DIP1_TP3_Q4_Startup_Delay, 2)

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
        
                self.suite.form.append_text_line("Detected delay of %ims" % delay_ms)
                self.suite.form.append_text_line("Tablet USB voltage (AD2) is {}".format(Channel(AD2_Tablet_USB_Volts).read_voltage()))
                self.suite.form.append_text_line("External USB voltage (AD6) is {}".format(Channel(AD6_External_USB_Volts).read_voltage()))

                # We leave it up to the user to decide whether the test fails or not.
                self.suite.form.enable_test_buttons()

                if delay_ms >= delay_lower and delay_ms <= delay_higher:
                    self.suite.form.append_text_line("Delay of %ims is within bounds (%ims to %ims), test passed." % delay_ms, delay_lower, delay_higher)
                else:
                    self.suite.form.append_text_line("WARNING: Delay of %ims is out of bounds (between %ims and %ims)" % delay_ms, delay_lower, delay_higher)

                #self.suite.form.append_text_line("\nWait for LED D1 to go RED before proceeding!")

            else:
                self.suite.form.append_text_line("Awaiting DIP1 low timed out. Press RESET to try again.")
                self.suite.form.disable_pass_button()

class Test1b_PogoPowerInput(TestProcedure):
    """Pogo power input"""

    description = "1b. Pogo power input"

    def setUp(self):
        digio.set_high(DOP1_Tablet_Full_Load_Switch)

    def run(self):
        self.suite.form.set_text("Observe LED PCB D1 is RED and LOAD 1 LED is RED.")
        self.log_failure("User indicated LED PCB D1 is not illuminated", False)

class Test1c_ChargeBatteryStep1(TestProcedure):
    """Pogo power to battery board"""

    description = "1c. Charge Battery (Step 1)"

    def run(self):

        bound_lower = 4.8
        bound_higher = 5.2

        ad3 = Channel(AD3_Batt_Board_Power_In_Volts)
        valid, voltage = ad3.voltage_between(bound_lower, bound_higher, 0.01)

        text = "Detected +{}v on battery board (AD3)."

        if not valid:
            text += "\n\nWARNING: This voltage is OUTSIDE of the required bounds (>= %i and <= %i)" % bound_lower, bound_higher

        text += "\n\nConfirm LED D5 is illuminated solid RED"
        text += "\n\nConfirm LED D2 is OFF completely"
        text += "\n\nLED D4 can be ignored."
        text += "\n\nIf D2 has illuminated, or D5 is flashing, replace battery PCB and start from beginning (ABORT button)"

        self.suite.form.set_text(text.format(voltage))
        self.log_failure("User indicated LED D5 is NOT illuminated solid red and/or D2 is illuminated", False)
        
class Test1c_ChargeBatteryStep2(TestProcedure):
    """Measure pogo power voltage divider"""

    description = "1c. Charge Battery (Step 2)"
    auto_advance = True

    def run(self):

        ad4_first_measure = 4.5
        ad4_second_lower = 2.0
        ad4_second_higher = 3.0

        ad5_lower = 3.0
        ad5_higher = 4.7

        self.suite.form.set_text("Reading voltage on AD4")
        ad4 = Channel(AD4_Batt_Board_Temp_Sense_Cutoff)

        if ad4.read_voltage() < ad4_first_measure:
            self.suite.form.append_text_line("Voltage is less than %iv" % ad4_first_measure)

            self.suite.form.append_text_line("Checking voltage on AD4 is between %iv and %iv" % ad4_second_lower, ad4_second_higher)
            valid, volts = ad4.voltage_between(ad4_second_lower, ad4_second_higher, 0.01)

            if valid:
                self.suite.form.append_text_line("Voltage %.2f is in bounds" % volts)

                ad5 = Channel(AD5_Batt_Board_Battery_Volts)
                self.suite.form.append_text_line("Checking if AD5 voltage is between %iv and %iv" % ad5_lower, ad5_higher)

                valid, volts = ad5.voltage_between(ad5_lower, ad5_higher, 0.01)

                if valid:
                    self.suite.form.append_text_line("Battery PCB voltage is %.2f, test passed." % volts)
                    self.set_passed()
                    """
                    if volts > 3.9:
                        self.suite.form.append_text_line("Voltage is above 3.9v, please change battery and reset test")
                    else:
                        self.suite.form.append_text_line("Battery PCB voltage is %.2f, test passed." % volts)
                        self.set_passed()
                    """

                else:
                    self.log_failure("Battery PCB voltage is %.2f, test failed." % volts)
                    self.set_failed()
            else:
                self.log_failure("Voltage %.2f is OUT OF BOUNDS, test failed." % volts)
                self.set_failed()
        else:
            self.log_failure("Voltage is greater than %iv, test failed" % ad4_first_measure)
            self.set_failed()

class Test1d_TabletChargedStep1(TestProcedure):

    description = "1d. Tablet Charged (Step 1)"
    enable_pass_fail = False

    def run(self):
        
        self.suite.form.set_text("Turn BATTERY OFF. Press PASS when completed.")
        self.set_passed()

class Test1d_TabletChargedStep2(TestProcedure):
    """Check tablet charged"""

    description = "1d. Tablet Charged"

    def run(self):
        
        digio.set_low(DOP1_Tablet_Full_Load_Switch)
        digio.set_high(DOP2_Tablet_Charged_Load_Switch)

        self.suite.form.set_text("Observe LED PCB D1 is GREEN or ORANGE and LOAD 2 LED is RED.")
        self.log_failure("User indicated LED PCB D1 is not illuminated or RED", False)
        

class Test2a_BatteryBoardPowersTabletStep1(TestProcedure):
    """Battery PCB and USB PCB Test"""

    description = "2a. Battery board powers tablet (Step 1)"
    enable_pass_fail = False

    def setUp(self):
        digio.set_low(DOP2_Tablet_Charged_Load_Switch)

    def run(self):

        self.suite.form.set_text("Turn BATTERY ON\n\nTurn off Pogo Power (SW1) after BATTERY ON.\n\nPress PASS when completed.")
        self.set_passed()

class Test2a_BatteryBoardPowersTabletStep2(TestProcedure):

    description = "2a. Battery board powers tablet (Step 2)"
    auto_advance = True

    def setUp(self):
        time.sleep(1)

    def run(self):

        ad2_first_lower = 4.75
        ad2_first_higher = 5.0

        ad2_second_lower = 4.65
        ad2_second_higher = 4.85

        self.suite.form.set_text("Testing battery and USB PCBs")

        ad2 = Channel(AD2_Tablet_USB_Volts)
        valid, volts = ad2.voltage_between(ad2_first_lower, ad2_first_higher, 0.01)

        if valid:
            self.suite.form.append_text_line("Measured {}v on AD2 between bounds {}v and {}v, applying LOAD 2".format(volts, ad2_first_lower, ad2_first_higher))

            digio.set_high(DOP2_Tablet_Charged_Load_Switch)

            # Sleep 1 for 1 second before 
            time.sleep(1)
            
            valid, volts = ad2.voltage_between(ad2_second_lower, ad2_second_higher, 0.1)
            if valid:
                self.suite.form.append_text_line("Measured {}v on AD2, between bounds of {}v and {}v after LOAD 2 applied, test passed".format(volts, ad2_second_lower, ad2_second_higher))
                self.set_passed()
            else:
                self.log_failure("Measured {}v on AD2, OUT OF BOUNDS between {}v and {}. Test failed".format(volts, ad2_second_lower, ad2_second_higher))
                self.set_failed()

        else:
            self.log_failure("Measured {}v on AD2, OUT OF BOUNDS between {}v and {}v. Test failed".format(volts, ad2_first_lower, ad2_first_higher))
            self.set_failed()

class Test2b_PogoPinsIsolatedFromBatteryPower(TestProcedure):

    description = "2b. Pogo Pins isolated from Battery Power"
    auto_advance = True

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

        self.suite.form.set_text("Observe LED PCB (D1) is off while not in charge state before OTG power.\n\nNo illumination = PASS. Green or red illumination = FAIL")
        self.log_failure("User indicated LED PCB (D1) is illuminated, should be off", False)


class Test2d_BattBoardPowerInputViaPogoDisconnected(TestProcedure):

    description = "2d. Battery Board power input via PoGo disconnected"
    auto_advance = True

    def run(self):

        self.suite.form.set_text("Checking battery board power via PoGo is disconnected")
        ad3 = Channel(AD3_Batt_Board_Power_In_Volts)

        if ad3.zero_voltage():
            self.suite.form.append_text_line("Measured nominally zero volts on AD3. Test passed")
            self.set_passed()
        else:
            self.log_failure("Voltage detected on AD3, test failed.")
            self.set_failed()

class Test3a_ActivationOfOTGPowerStep1(TestProcedure):

    description = "3a. Activation of On The Go power (Step 1)"
    enable_pass_fail = False

    def setUp(self):
        digio.set_low(DOP2_Tablet_Charged_Load_Switch)

    def run(self):

        self.suite.form.set_text("Turn off BATTERY. Press PASS when action completed.")
        self.set_passed()
        

class Test3a_ActivationOfOTGPowerStep2(TestProcedure):

    description = "3a. Activation of On The Go power (Step 2)"
    auto_advance = True

    def run(self):

        self.suite.form.set_text("Test activation of On The Go (OTG) power")

        digio.set_output(DOP3_OTG_Mode_Trigger)
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
    auto_advance = True

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
        self.suite.form.set_text("Observe LED PCB (D1) is off while not in charge state after OTG power.\n\nNo illumination = PASS. Green or red illumination = FAIL")
        self.log_failure("User indicated LED PCB (D1) is illuminated, should be off", False)


class Test3d_BattBoardPowerInputViaPogoDisconnected(TestProcedure):

    description = "3d. Battery board power input via PoGo disconnected"
    auto_advance = True

    def run(self):

        self.suite.form.set_text("Checking battery board input isolation")

        ad3 = Channel(AD3_Batt_Board_Power_In_Volts)

        if ad3.read_voltage() < 1.0:
            self.suite.form.append_text_line("Measured nominally zero volts on AD3. Test passed")
            self.set_passed()
        else:
            self.log_failure("Voltage detected ({}v) on AD3. Battery board power input should be disconnected. Test failed.".format(ad3.read_voltage()))
            self.set_failed()

class Test3e_PCBRev3dSkip(TestProcedure):

    description = "3e. External battery voltage presented to tablet +VE"
    enable_pass_fail = False

    def run(self):
        
        self.suite.form.set_text("This test must be skipped for POGO PCB Rev 3d. Press PASS to continue.")
        self.set_passed()

# These tests are currently skipped for PCB rev 3d. Skip to test 3f.
class Test3e_NoExternalBattVoltageToTabletStep1(TestProcedure):

    description = "3e. External battery voltage presented to tablet +VE (Step 1)"
    enable_pass_fail = False

    def run(self):

        self.suite.form.set_text("Turn BATTERY ON.\n\nConnect black ATE USB flylead and press PASS when completed.")
        self.set_passed()

class Test3e_NoExternalBattVoltageToTabletStep2(TestProcedure):

    description = "3e. External battery voltage presented to tablet +VE (Step 2)"
    auto_advance = True

    def run(self):

        ad7_lower = 4.84
        ad7_higher = 5.0

        self.suite.form.set_text("Test battery isolation switch (SW1) and pogo PCB")
        self.suite.form.enable_test_buttons()
        ad7 = Channel(AD7_Pogo_Battery_Output)

        valid, voltage = ad7.voltage_between(ad7_lower, ad7_higher, 0.01)
        self.suite.form.append_text_line("Detected voltage: {}v on AD7".format(voltage))

        if valid:
            self.suite.form.append_text_line("Voltage is within bounds of {}v to {}v, passed.".format(ad7_lower, ad7_higher))
            self.set_passed()
        else:
            self.log_failure("Voltage was NOT within bounds of {}v to {}v. Test failed.".format(ad7_lower, ad7_higher))
            self.set_failed()

class Test3e_NoExternalBattVoltageToTabletStep3(TestProcedure):

    description = "3e. External battery voltage presented to tablet +VE (Step 3)"
    auto_advance = True

    def run(self):

        self.suite.form.set_text("Checking for zero voltage on AD7")

        ad7 = Channel(AD7_Pogo_Battery_Output)

        if ad7.zero_voltage():
            self.suite.form.append_text_line("Zero voltage detected on AD7, test passed")
            self.set_passed()
        else:
            self.suite.form.append_text_line("Voltage detected ({}v) on AD7, test failed. Check BATT-SW is toggled and press RESET.".format(ad7.read_voltage()))
            self.suite.form.append_text_line("If BATT-SW is toggled, the test has failed.")
            self.set_failed()
# End skipped tests.


class Test3f_USBCableContinuityTestStep1(TestProcedure):

    description = "3f. USB cable continuity for data transfer (Step 1)"
    enable_pass_fail = False

    def run(self):
        self.suite.form.set_text("Turn battery switch (SW5) off if already on.\n\nConnect black ATE USB flylead.\n\nPress PASS when completed.")
        self.set_passed()

class Test3f_USBCableContinuityTestStep2(TestProcedure):

    description = "3f. USB cable continuity for data transfer (Step 2)"
    auto_advance = True

    def run(self):

        self.suite.form.set_text("Measuring continuity on USB data lines")

        got_Dplus = False
        got_Dminus = False

        digio.set_high(DOP4_Dplus_Ext_USB)
        if digio.await_high(DIP3_Dplus_Tablet_USB_Sense, 2):
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
        if digio.await_high(DIP4_Dminus_Tablet_USB_Sense, 2):
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
    enable_pass_fail = False

    def run(self):
        self.suite.form.set_text("All tests finished. Press PASS to display the test summary.")
        self.set_passed()