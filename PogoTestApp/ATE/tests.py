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

class Test_Setup1(TestProcedure):

    description = "Setup 1 of 2"
    enable_pass_fail = False

    def run(self):
        txt = """Before starting, please ensure:

- Applicable PCBs are installed.
- PSU_pogo, PSU_ATE and battery simulator PSU are connected and switched on.
- Transport manual switch is OFF.

Tap PASS to confirm.
"""

        self.suite.form.set_text(txt)
        self.set_passed();


class Test_Setup2(TestProcedure):

    description = "Setup 2 of 2"
    enable_pass_fail = False

    def run(self):
        txt = """Action:
SW_BAT_sim to be turned on
POGO_SW to be turned on"""
    
        self.suite.form.set_text(txt)
        self.set_passed()

class TestPWR_1(TestProcedure):

    description = "Power Management PCB - Pin Test"
    enable_pass_fail = False
    auto_advance = True

    def run(self):
        digio.set_low(digio.outputs)
        digio.set_high(DOP6_T_SW_ON)

        digio.await_high(DIP1_PWRUP_Delay)
        
        inputs = digio.read_all_inputs()

        expected_values = {
            DIP1_PWRUP_Delay: 1,
            DIP2_OTG_OK: 0,
            DIP3_Dplus_J5_3_OK: 0,
            DIP4_Dminus_J5_2_OK: 0,
            DIP5_5V_PWR: 1,
            DIP6_From_J7_4: 0,
            DIP7_J3_LINK_OK: 1,
            DIP8_LED_RD: 1,
            DIP9_LED_GN: 0,
            DIP10_USB_PERpins_OK: 0,
            DIP11_5V_ATE_in: 1
        }

        if (inputs != expected_values):
            self.suite.form.set_text("Input DIP values don't match expected.")
            self.set_failed()
        else:
            self.set_passed()

class TestPWR_2(TestProcedure):

    description = "Power Management PCB - Power Up Delay"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        ad1 = Channel(AD1_V_pogo)
        ad5 = Channel(AD5_V_bat)
        ad7 = Channel(AD7_V_sys_out)
        ad8 = Channel(AD8_V_out)

        if ad5.voltage_between(0, 1.50) and ad7.voltage_between(0, 2.00) and ad8.voltage_between(0, 2.00):

            digio.set_high(DOP12_BAT1_GPIO)
            
            if ad5.voltage_between(3.95, 4.25) and ad7.voltage_between(4.90, 5.15) and ad8.voltage_between(4.85, 5.10):
                self.set_passed()
            else:
                self.suite.form.set_text("Voltages for AD5, AD7 or AD8 were not within tolerable values (DOP12 high)")
                self.set_failed()

        else:
            self.suite.form.set_text("Voltages for AD5, AD7 or AD8 were not within tolerable values (DOP12 low)")
            self.set_failed()

        digio.set_high(DOP11_POGO_ON_GPIO)

        if ad1.voltage_between(0, 2.00) and ad8.voltage_between(4.85, 5.10):

            time.sleep(0.1)
            digio.set_low(DOP11_POGO_ON_GPIO)

            low_passed, low_delay = digio.await_low(DIP1_PWRUP_Delay)
            high_passed, high_delay = digio.await_high(DIP1_PWRUP_Delay)

            delay = low_delay + high_delay

            if (low_passed and high_passed) and (delay > 0.5 and delay < 1.0):
                if (ad1.voltage_between(4.90, 5.10) and ad8.voltage_between(4.85, 5.10)):
                    self.set_passed()
                else:
                    self.log_failure("AD1 or AD8 voltage not within limits")
            else:
                self.log_failure("DIP1 low or high out of tolerance, or delay < 500ms or > 1000ms")
        else:
            self.log_failure("AD1 voltage > 2.00v or AD8 out of bounds")

class TestPWR_3(TestProcedure):

    description = "Power Management PCB - Back up mode"
    enable_pass_fail = False
    auto_advance = True

    def run(self):
        
        ad5 = Channel(AD5_V_bat)
        ad6 = Channel(AD6_V_sense)
        ad7 = Channel(AD7_V_sys_out)
        ad8 = Channel(AD8_V_out)
        
        digio.set_low([DOP12_BAT1_GPIO, DOP13_BAT0_GPIO, DOP2_Discharge_Load])

        if (ad5.voltage_near(2.64, 0.2) and 
            ad6.voltage_near(1.57, 0.2) and 
            ad7.voltage_between(0, 1.50) and 
            ad8.voltage_between(0, 1.50)):
            
            digio.set_high(DOP13_BAT0_GPIO)
            
            if (ad5.voltage_near(3.35, 0.1) and 
                ad6.voltage_near(2.0, 0.2) and 
                ad7.voltage_near(5.0, 0.15) and 
                ad8.voltage_between(0, 1.50)):
                
                digio.set_low(DOP13_BAT0_GPIO)
                digio.set_high(DOP12_BAT1_GPIO)

                if (ad5.voltage_near(4.09, 0.1) and
                    ad6.voltage_near(2.42, 0.2) and
                    ad7.voltage_near(5.0, 0.15) and
                    ad8.voltage_near(5.0, 0.15)):

                    digio.set_high(DOP2_Discharge_Load)

                    if (ad5.voltage_near(4.08, 0.1) and
                        ad6.voltage_near(3.73, 0.2) and
                        ad7.voltage_near(4.9, 0.15) and
                        ad8.voltage_near(4.9, 0.15)):

                        self.set_passed()

class TestPWR_4(TestProcedure):

    description = "Power Management PCB - Normal mode test"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        digio.set_low(digio.outputs)
        digio.set_high(DOP6_T_SW_ON)

        time.sleep(0.02)

        ad5 = Channel(AD5_V_bat)
        ad6 = Channel(AD6_V_sense)
        ad8 = Channel(AD8_V_out)

        if (ad5.voltage_near(2.56, 0.2) and
            ad6.voltage_near(1.18, 0.3) and
            ad8.voltage_near(5.00, 0.15)):

            digio.set_high(DOP13_BAT0_GPIO)

            if (ad5.voltage_near(4.05, 0.1) and
                ad6.voltage_between(0, 0.2) and
                ad8.voltage_between(4.90, 0.2)):

                digio.set_low(DOP12_BAT1_GPIO)
                digio.set_high(DOP13_BAT0_GPIO)

                if (ad5.voltage_near(4.10, 0.1) and
                    ad6.voltage_near(1.40, 0.3) and
                    ad8.voltage_near(4.90, 0.2)):

                    digio.set_high(DOP12_BAT1_GPIO)

                    if (ad5.voltage_near(4.35, 0.1) and
                        ad6.voltage_near(2.62, 0.3) and 
                        ad8.voltage_near(5.0, 0.2)):

                        self.set_passed()

                    else:
                        self.log_failure("Voltages in stage 4 out of tolerance")

                else:
                    self.log_failure("Voltages in stage 3 out of tolerance")

            else:
                self.log_failure("Voltages in stage 2 out of tolerance")

        else:
            self.log_failure("Voltages in stage 1 out of tolerance")


class TestPWR_5(TestProcedure):

    description = "Power Management PCB - Thermal protection test"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        ad3 = Channel(AD3_V_in)
        ad4 = Channel(AD4_V_TP13_NTC)
        ad6 = Channel(AD6_V_sense)

        digio.set_low(digio.outputs)
        digio.set_high(DOP6_T_SW_ON)
        digio.set_high(DOP12_BAT1_GPIO) # not sure if this should be high or low, to be checked.


        digio.set_high(DOP13_BAT0_GPIO)

        if (ad3.voltage_near(4.9, 0.2) and
            ad4.voltage_between((ad3.read_voltage() * 0.3), (ad3.read_voltage() * 0.75)) and
            ad6.voltage_between(0, 0.2)):

            digio.set_high(DOP7_Cold_sim)

            if (ad3.voltage_near(4.9, 0.2) and
                ad4.read_voltage() > (ad3.read_voltage() * 0.75) and
                ad6.voltage_near(2.0, 0.2)):

                digio.set_low(DOP7_Cold_sim)
                digio.set_high(DOP8_Hot_sim)

                if (ad3.voltage_near(4.9, 0.2) and
                    ad4.read_voltage() < (ad3.read_voltage() * 0.3) and
                    ad6.voltage_near(2.0, 0.2)):

                    digio.set_low(DOP8_Hot_sim)

                    if (ad3.voltage_near(4.9, 0.2) and
                        ad4.voltage_between((ad3.read_voltage() * 0.3), (ad3.read_voltage() * 0.75)) and
                        ad6.voltage_between(0, 0.2)):

                        self.set_passed()
                    else:
                        self.log_failure("Stage 4 tolerances out of range")
                else:
                    self.log_failure("Stage 3 tolerances out of range")
            else:
                self.log_failure("Stage 2 tolerances out of range")
        else:
            self.log_failure("Stage 1 tolerances out of range")


class TestPWR_6(TestProcedure):

    description = "Power Management PCB - Reset"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        digio.set_low(digio.outputs)
        digio.set_high(DOP11_POGO_ON_GPIO)


class TestCON_1a(TestProcedure):

    description = "Connection PCB - Digital Read (1 of 2)"
    enable_pass_fail = False
    auto_advance = False

    def run(self):

        if self.suite.selected_suite == 0:
            self.suite.form.append_text_line("Turn SW_1.25A to ON")
        if self.suite.selected_suite == 1:
            self.suite.form.append_text_line("Turn SW_0.8A to ON")
        if self.suite.selected_suite == 2:
            self.suite.form.append_text_line("Turn SW_1.14A to ON")
        if self.suite.selected_suite == 3:
            self.suite.form.append_text_line("Turn SW_0.36A to ON")

        self.set_passed()

class TestCON_1b(TestProcedure):

    description = "Connection PCB - Digital Read (2 of 2)"
    enable_pass_fail = False
    auto_advance = True
    
    def run(self):

        digio.set_low(digio.outputs)
        digio.set_high(DOP6_T_SW_ON)

        expected_inputs = {
            DIP1_PWRUP_Delay: 1,
            DIP2_OTG_OK: 0,
            DIP3_Dplus_J5_3_OK: 0,
            DIP4_Dminus_J5_2_OK: 0,
            DIP5_5V_PWR: 1,
            DIP6_From_J7_4: 0,
            DIP7_J3_LINK_OK: 1,
            DIP8_LED_RD: 1,
            DIP9_LED_GN: 0,
            DIP10_USB_PERpins_OK: 1,
            DIP11_5V_ATE_in: 1
        }

        if digio.read_all_inputs == expected_inputs:
            self.set_passed()
        else:
            self.log_failure("Digital inputs not as expected")

class TestCON_2(TestProcedure):

    description = "Connection PCB - Analogue Read"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        ad6 = Channel(AD6_V_sense)

        if (ad6.voltage_between(0, 0.02) and
            digio.read(DIP9_LED_GN) == 0 and
            digio.read(DIP8_LED_RD) == 1):

            digio.set_high(DOP1_Load_ON)

            if self.suite.selected_suite == 0:
                if ad6.voltage_between(2.48, 2.79) and (digio.read(DIP9_LED_GN) == 1 and
                digio.read(DIP8_LED_RD) == 0):
                    self.set_passed()
                else:
                    self.log_failure("Voltage out of bounds")
            
            if self.suite.selected_suite == 1:
                if ad6.voltage_between(1.44, 1.74) and (digio.read(DIP9_LED_GN) == 1 and
                digio.read(DIP8_LED_RD) == 0):
                    self.set_passed()
                else:
                    self.log_failure("Voltage out of bounds")

            if self.suite.selected_suite == 2:
                if ad6.voltage_between(2.26, 2.54) and (digio.read(DIP9_LED_GN) == 1 and
                digio.read(DIP8_LED_RD) == 0):
                    self.set_passed()
                else:
                    self.log_failure("Voltage out of bounds")

            if self.suite.selected_suite == 3:
                if ad6.voltage_between(0.74, 0.94) and (digio.read(DIP9_LED_GN) == 1 and
                digio.read(DIP8_LED_RD) == 0):
                    self.set_passed()
                else:
                    self.log_failure("Voltage out of bounds")
        else:
            self.log_failure("Voltage out of bounds")   
                

class TestCON_3(TestProcedure):

    description = "Connection PCB - USB Data Lines"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        digio.set_high(DOP4_TP5_GPIO)
        digio.set_low(DOP5_TP6_GPIO)
        digio.set_high(DOP3_TP7_GPIO)

        if (digio.read(DIP4_Dminus_J5_2_OK) == 1 and
            digio.read(DIP3_Dplus_J5_3_OK) == 1 and
            digio.read(DIP2_OTG_OK)) == 1:

            digio.set_low(DOP3_TP7_GPIO)

            if (digio.read(DIP4_Dminus_J5_2_OK) == 1 and
                digio.read(DIP3_Dplus_J5_3_OK) == 0 and
                digio.read(DIP2_OTG_OK) == 0):

                digio.set_low(DOP4_TP5_GPIO)
                digio.set_high(DOP5_TP6_GPIO)
                digio.set_high(DOP3_TP7_GPIO)

                if (digio.read(DIP4_Dminus_J5_2_OK) == 1 and
                    digio.read(DIP3_Dplus_J5_3_OK) == 1 and
                    digio.read(DIP2_OTG_OK)) == 1:

                    digio.set_low(DOP4_TP5_GPIO)
                    digio.set_low(DOP3_TP7_GPIO)

                    if (digio.read(DIP4_Dminus_J5_2_OK) == 0 and
                        digio.read(DIP3_Dplus_J5_3_OK) == 1 and
                        digio.read(DIP2_OTG_OK)) == 0:

                        self.set_passed()

                    else:
                        self.log_failure("Digital I/O unexpected result")
                else:
                    self.log_failure("Digital I/O unexpected result")
            else:
                self.log_failure("Digital I/O unexpected result")
        else:
            self.log_failure("Digital I/O unexpected result")


class TestCON_4(TestProcedure):

    description = "Connection PCB - Ethernet filter"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        digio.set_high(DOP10_FLT_loop_back)
        digio.set_high(DOP9_TO_J7_1)

        if digio.read(DIP6_From_J7_4) == 1:
            digio.set_low(DOP9_TO_J7_1)
            if digio.read(DIP6_From_J7_4) == 0:
                digio.set_low(DOP10_FLT_loop_back)
                digio.set_high(DOP9_TO_J7_1)
                if digio.read(DIP6_From_J7_4) == 0:
                    digio.set_low(DOP9_TO_J7_1)
                    if digio.read(DIP6_From_J7_4) == 0:
                        self.set_passed()
                    else:
                        self.log_failure("DIP6 unexpected value")
                else:
                    self.log_failure("DIP6 unexpected value")
            else:
                self.log_failure("DIP6 unexpected value")
        else:
            self.log_failure("DIP6 unexpected value")


class TestCON_5(TestProcedure):

    description = "Connection PCB - Complete"
    enable_pass_fail = False
    auto_advance = True

    def run(self):

        digio.set_low(digio.outputs)
        digio.set_high(DOP11_POGO_ON_GPIO)


class TestEnd_TestsCompleted(TestProcedure):
    
    description = "Testing completed"
    enable_pass_fail = False

    def run(self):
        self.suite.form.set_text("All tests finished. Press PASS to display the test summary.")
        self.set_passed()
