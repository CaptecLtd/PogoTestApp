import time
import random
from datetime import datetime, timedelta

from ATE.suite import TestSuite
from ATE.adc import Channel
import ATE.digio as digio
import ATE.adc as adc
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

class Test00_Setup(TestProcedure):

    description = "Setup 1 of 2"
    enable_pass_fail = False

    def run(self):
        txt = """Ensure:
Transport switch - OFF
J2 on power management board connected to J2_pwr on ATE
J6_CON connected to J6 on connection board
J2_CON connected to J2 on connection board
J7_CON is mated with J7 housing from connection board
J4_micro USB and J5_tablet USB connected to J4 and J5 on connection board"""

        self.suite.form.set_text(txt)
        self.set_passed();


class Test01_Setup(TestProcedure):

    description = "Setup 2 of 2"
    enable_pass_fail = False

    def run(self):
        txt = """Action:
SW_BAT_sim to be turned on
POGO_SW to be turned on"""
    
        self.suite.form.set_text(txt)
        self.set_passed()

class Test02_Rev01(TestProcedure):

    description = "Load Switch (4950-060-10-01)"
    enable_pass_fail = False

    def run(self):
        
        self.suite.form.set_text("Turn on SW_1.25A")
        self.set_passed()

class Test02_Rev02(TestProcedure):

    description = "Load Switch (4950-060-10-02)"
    enable_pass_fail = False

    def run(self):
        
        self.suite.form.set_text("Turn on SW_0.8A")
        self.set_passed()

class Test02_Rev03(TestProcedure):

    description = "Load Switch (4950-060-10-03)"
    enable_pass_fail = False

    def run(self):
        
        self.suite.form.set_text("Turn on SW_1.13A")
        self.set_passed()

class Test02_Rev04(TestProcedure):

    description = "Load Switch (4950-060-10-04)"
    enable_pass_fail = False

    def run(self):
        
        self.suite.form.set_text("Turn on SW_0.36A")
        self.set_passed()

class TestB2_FirstStage(TestProcedure):

    description = "First stage test"

    def run(self):

        digio.set_high(DOP11_POGO_ON_GPIO)
    
        dig_inputs = digio.read_all_inputs()
        dig_expected = {
            "DIP1": 1,
            "DIP2": 0,
            "DIP3": 0,
            "DIP4": 0,
            "DIP5": 1,
            "DIP6": 0,
            "DIP7": 0,
            "DIP8": 1,
            "DIP9": 0,
            "DIP10": 1,
            "DIP11": 1
        }

        if self.suite.selected_suite == 0 or self.suite.selected_suite == 2:
            dig_expected["DIP7"] = 1

        if dig_inputs == dig_expected:
            self.set_passed()
        else:
            self.suite.form.set_text("Failure on power up")
            if dig_inputs["DIP1"] == 0:
                self.suite.form.append_text("Output failure")
            if dig_inputs["DIP5"] == 0:
                self.suite.form.append_text("Pogo failed to turn on")
            if (self.suite.selected_suite == 0 or self.suite.selected_suite == 2) and dig_inputs["DIP7"] == 0:
                self.suite.form.append_text("Link LK3 was not made")
            if (self.suite.selected_suite == 1 or self.suite.selected_suite == 3) and dig_inputs["DIP7"] == 1:
                self.suite.form.append_text("Incorrect version entered?")
            if dig_inputs["DIP10"] == 0:
                self.suite.form.append_text("Fault with J4 and J5 connectors")
            if dig_inputs["DIP11"] == 0:
                self.suite.form.append_text("Error with ATE")
            self.set_failed()

        # Handle ADC channels
        channels = adc.get_all_channels()
        adc_error = False

        ad1b, ad1v = channels["AD1"].voltage_between(4.8, 5.2, 0.01)
        if not ad1b:
            self.suite.form.append_text("AD1: %d is out of bounds (>= 4.8, <= 5.2)" % ad1v)
            adc_error = True

        ad2b, ad2v = channels["AD2"].voltage_between(4.8, 5.2, 0.01)
        if not ad2b:
            self.suite.form.append_text("AD2: %d is out of bounds (>= 4.8, <= 5.2)" % ad2v)
            adc_error = True

        ad3b, ad3v = channels["AD3"].voltage_between(4.8, 5.2, 0.01)
        if not ad3b:
            self.suite.form.append_text("AD3: %d is out of bounds (>= 4.8, <= 5.2)" % ad3v)
            adc_error = True

        ad4b, ad4v = channels["AD4"].voltage_between(1.8, 3.2, 0.01)
        if not ad4b:
            self.suite.form.append_text("AD4: %d is out of bounds (>= 1.8, <= 3.2)" % ad4v)
            adc_error = True

        ad5b, ad5v = channels["AD5"].voltage_between(0.2, 1.5, 0.01)
        if not ad5b:
            self.suite.form.append_text("AD5: %d is out of bounds (>= 0.2, <= 1.5)" % ad5v)
            adc_error = True
    
        ad6b, ad6v = channels["AD6"].voltage_between(0.2, 0.5, 0.01)
        if not ad6b:
            self.suite.form.append_text("AD6: %d is out of bounds (>= 0.2, <= 0.5)" % ad6v)
            adc_error = True

        ad7b, ad7v = channels["AD7"].voltage_between(0.1, 1.5, 0.01)
        if not ad7b:
            self.suite.form.append_text("AD7: %d is out of bounds (>= 0.1, <= 1.5)" % ad7v)
            adc_error = True

        ad8b, ad8v = channels["AD8"].voltage_between(4.75, 5.15, 0.01)
        if not ad8b:
            self.suite.form.append_text("AD8: %d is out of bounds (>= 4.75, <= 5.15)" % ad8v)
            adc_error = True

        if adc_error:
            self.set_failed()
        else:
            self.set_passed()

class TestB3_1_PowerMgmt_CheckIO(TestProcedure):

    description = "Power Management Board - I/O Check"

   

class TestB3_2_PowerMgmt_CheckPowerUp(TestProcedure):

    description = "Power Management Board - Power Up Check"

class TestB3_3_PowerMgmt_BackupMode(TestProcedure):

    description = "Power Management Board - Backup Mode Test"

class TestB3_4_PowerMgmt_NormalMode(TestProcedure):

    description = "Power Management Board - Normal Mode Test"

class TestB3_5_PowerMgmt_ThermalProtection(TestProcedure):

    description = "Power Management Board - Thermal Protection"

class TestB4_1_ConnectionBoard_LineQuality(TestProcedure):

    description = "Connection Board - Line Quality"
        

class TestEnd_TestsCompleted(TestProcedure):
    
    description = "Testing completed"
    enable_pass_fail = False

    def run(self):
        self.suite.form.set_text("All tests finished. Press PASS to display the test summary.")
        self.set_passed()