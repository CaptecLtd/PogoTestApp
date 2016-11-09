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

class Test0a_ConnectHardwareAndAwaitPowerOn(TestProcedure):
    description = "0a. Connect PCBA & cable set to test station"

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

        # We have a voltage and it's 5v(ish)
        if got_5v:
            self.suite.pass_test()
        # Not got 5v and/or timeout reached.
        else:
            self.suite.form.enable_test_buttons()
            self.suite.form.set_text("Pogo input volts ({}) was outside of expected parameter (5.0v)".format(ch1.read_voltage()))


class Test1a_MeasurePowerOnDelay(TestProcedure):
    """AD1 volts applied, wait DIP1 high then count to DIP1 low"""

    description = "1a. Power on delay from pogo power to tablet power (400-600ms)"

    def run(self):

        self.suite.form.set_text("Waiting for DIP1 to become high")

        dip1_high = digio.await_high(DIP1_TP3_Q4_Startup_Delay)

        if not dip1_high:
            self.suite.form.append_text_line("DIP1 did not become high, cannot measure power on delay.")
            self.suite.fail_test()
            return

        before = datetime.now()

        got_low = digio.await_low(DIP1_TP3_Q4_Startup_Delay)

        if got_low:
            after = datetime.now()
            span = (after - before)

            delay_ms = span.total_seconds() * 1000
        
            self.suite.append_text("Detected delay of %ims" % delay_ms)
            self.suite.append_text("Tablet USB voltage is %d" % (Channel(AD2_Tablet_USB_Volts).read_voltage()))
            self.suite.append_text("External USB voltage is %d" % (Channel(AD6_External_USB_Volts).read_voltage()))
            
            self.suite.form.enable_test_buttons()

            if delay_ms >= 400 and delay_ms <= 600:
                self.suite.append_text("Delay of {}ms is within bounds (400ms to 600ms)".format(delay_ms))
            else:
                self.suite.append_text("WARNING: Delay of {}ms is out of bounds (between 400ms and 600ms)".format(delay_ms))

        else:
            self.suite.form.append_text_line("Awaiting DIP1 low timed out.")

class Test1b_PogoPowerInput(TestProcedure):
    """Pogo power input"""

    description = "1b. Pogo power input"

    def setUp(self):
        digio.set_high(DOP1_Tablet_Full_Load_Switch)

    def run(self):
        self.suite.form.enable_test_buttons()
        self.suite.form.set_text("Observe LED PCB D1 is RED")

class Test1c_ChargeBatteryStep1(TestProcedure):
    """Pogo power to battery board"""

    description = "1c. Charge Battery (Step 1)"

    def run(self):

        ch3 = Channel(AD3_Batt_Board_Power_In_Volts)
        valid, voltage = ch3.voltage_between(4.95, 5.05, 0.01)

        text = "Detected +{}V on battery board."
        text += "\n\nConfirm LED D5 is illuminated RED"
        text += "\nConfirm LEDs D2 and D4 are OFF completely"
        text += "\n\nIf D2 or D4 have illuminated at all, fail the test"

        self.suite.form.set_text(text.format(voltage))
        
class Test1c_ChargeBatteryStep2(TestProcedure):
    """Measure pogo power voltage divider"""

    description = "1c. Charge Battery (Step 2)"

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

class Test1d_TabletCharged(TestProcedure):
    """Check tablet charged"""

    description = "1d. Tablet Charged"

    def run(self):
        
        digio.set_low(DOP1_Tablet_Full_Load_Switch)
        digio.set_high(DOP2_Tablet_Charged_Load_Switch)

        self.suite.set_text("Observe LED D1 illuminated GREEN")
        

class Test2a_BatteryBoardPowersTablet(TestProcedure):
    """Battery PCB and USB PCB Test"""

    description = "2a. Battery board powers tablet"

    def run(self):
        self.suite.form.set_text("Turn off Pogo Power (SW1) and turn on battery isolation switch (BATT-SW)")


class Test2b_PogoPinsIsolatedFromBatteryPower(TestProcedure):

    description = "2b. Pogo Pins isolated from Battery Power"

    def run(self):
        self.suite.form.set_text("Reading voltage from AD1, expecting 0V")

        ch = Channel(AD1_Pogo_Input_Volts)

        if ch.zero_voltage():
            self.suite.pass_test()
        else:
            self.suite.form.append_text_line("Got {}v from AD1, test failed".format(ch.read_voltage()))
            self.suite.fail_test()

class Test2c_LEDStatusNotInChargeState(TestProcedure):
    
    description = "2c. LED status (not in charge state)"

    def run(self):
        self.suite.form.enable_test_buttons()

        self.suite.form.set_text("Observe LED PCB (D1) is off. No illumination = PASS. Green or red illumination = FAIL")

    def tearDown(self):
        self.suite.form.disable_test_buttons()

class Test2d_BattBoardPowerInputViaPogoDisconnected(TestProcedure):

    description = "2d. Battery Board power input via PoGo disconnected"

    def run(self):
        ch = Channel(AD2_Tablet_USB_Volts)

        if ch.zero_voltage():
            self.suite.pass_test()
        else:
            self.suite.form.set_text("Voltage detected on AD2, test failed.")
            self.suite.fail_test()

class Test3a_ActivationOfOTGPower(TestProcedure):

    description = "3a. Activation of On The Go power"

    def run(self):
        digio.set_low(DOP3_OTG_Mode_Trigger)

        otg_triggered = digio.await_low(DIP2_Tablet_OTG_Sense)

        if otg_triggered:
            self.suite.pass_test()
        else:
            self.suite.form.set_text("OTG power was not detected on DIP2, test failed")
            self.suite.fail_test()

class Test3b_PogoPinsIsolatedFromOTGModePower(TestProcedure):

    description = "3b. Pogo pins isolated from tablet OTG mode power"

    def run(self):
        ch = Channel(AD1_Pogo_Input_Volts)

        if ch.zero_voltage():
            self.suite.pass_test()
        else:
            self.suite.form.set_text("Voltage detected ({}v) on AD1, OTG mode enabled so no pogo voltage (AD1) is expected".format(ch.read_voltage()))
            self.suite.fail_test()

class Test3c_LEDStatusNotInChargeState(TestProcedure):

    description = "3c. LED status (not in charge state)"

    def run(self):
        self.suite.form.enable_test_buttons()
        self.suite.form.set_text("Observe LED PCB (D1) is off. No illumination = PASS. Green or red illumination = FAIL")

    def tearDown(self):
        self.suite.form.disable_test_buttons()

class Test3d_BattBoardPowerInputViaPogoDisconnected(TestProcedure):

    description = "3d. Battery board power input via PoGo disconnected"

    def run(self):
        ch = Channel(AD3_Batt_Board_Power_In_Volts)

        if ch.zero_voltage():
            self.suite.pass_test()
        else:
            self.suite.form.set_text("Voltage detected ({}v) on AD3. Battery board power input should be disconnected. Test failed.")
            self.suite.fail_test()

class Test3e_NoExternalBattVoltageToTabletStep1(TestProcedure):

    description = "3e. No external battery voltage presented to tablet +VE (Step 1)"

    def run(self):
        ch = Channel(AD7_Pogo_Battery_Output)

        voltage = ch.read_voltage()
        self.suite.form.set_text("Detected voltage: {}v on AD7".format(voltage))

        if ch.voltage_between(4.84, 4.88, 0.01):
            self.suite.form.append_text_line("Voltage within bounds of 4.84v to 4.88v, passed.")
            self.suite.form.append_text_line("Toggle switch BATT-SW to isolate battery. PASS when completed.")
            self.suite.pass_test()
        else:
            self.suite.form.append_text_line("Voltage was NOT within bounds of 4.84v to 4.88v, failed")
            self.suite.fail_test()

class Test3e_NoExternalBattVoltageToTabletStep2(TestProcedure):

    description = "3e. No external battery voltage presented to tablet +VE (Step 2)"

    def run(self):
        ch = Channel(AD7_Pogo_Battery_Output)

        self.suite.form.enable_test_buttons()

        if ch.zero_voltage():
            self.suite.form.append_text_line("Zero voltage detected on AD7, test passed")
        else:
            self.suite.form.disable_pass_button()
            self.suite.form.append_text_line("Voltage detected ({}v) on AD7, test failed. Check BATT-SW is toggled and reset.")
            self.suite.form.append_text_line("If BATT-SW is toggled, FAIL the test.")

class Test3f_USBCableContinuityTest(TestProcedure):

    description = "3f. USB cable continuity for data transfer"

    def run(self):
        
        self.suite.form.set_text("Measuring continuity on USB data lines")
        got_Dplus = False
        got_Dminus = False

        digio.set_high(DOP4_Dplus_Ext_USB)
        if digio.await_high(DIP3_Dplus_Tablet_USB_Sense):
            digio.set_low(DOP4_Dplus_Ext_USB)
            if not digio.read(DIP3_Dplus_Tablet_USB_Sense):
                self.suite.form.append_text_line("D+ continuity OK")
                got_Dplus = True
            else:
                self.suite.form.append_text_line("D+ continuity did not return to low")
        else:
            self.suite.form.append_text_line("D+ no signal")

        digio.set_high(DOP5_Dminus_Ext_USB)
        if digio.await_high(DIP4_Dminus_Tablet_USB_Sense):
            digio.set_low(DOP5_Dminus_Ext_USB)
            if not digio.read(DIP4_Dminus_Tablet_USB_Sense):
                self.suite.form.append_text_line("D- continuity OK")
                got_Dminus = True
            else:
                self.suite.form.append_text_line("D- continuity did not return to low")
        else:
            self.suite.form.append_text_line("D- no signal")

        if got_Dminus and got_Dplus:
            self.suite.form.append_text_line("Continuity for D+ and D- OK, test passed")
        else:
            self.suite.form.append_text_line("Continuity error(s). Check data lines on USB")