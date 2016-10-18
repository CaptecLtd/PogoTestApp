import time
import random

from pogolib.suite import TestSuite, TestState


class Test(object):
    """Base test class"""

    # When set to true, failing the test will abort the suite.
    aborts = False

    state = TestState.not_run

    #suite = TestSuite

    def run(self):
        pass

    def set_passed(self):
        self.state = TestState.passed

    def set_failed(self):
        self.state = TestState.failed

    def reset(self):
        self.state = TestState.not_run

class MeasurePowerOnDelay(Test):
    """Pogo power on delay"""

    def run(self):
        self.suite.set_text("Please turn on LOAD 1. (this sample just simulates the switch being flipped)")
        self.suite.form.disable_test_buttons()

        delay = 0
        while delay < 100:
            time.sleep(0.1)
            self.suite.form.update()
            delay += 1

        self.suite.set_text("Got load, measuring tablet power delay")
        
        # Simulated wait for power.
        random.seed()
        delay = random.randint(200,1200)
        time.sleep( delay / 1000)
        
        self.suite.set_text("Detected delay of %ims" % delay)

        self.suite.form.enable_test_buttons()

class PogoPowerInput(Test):
    """Pogo power input"""

    aborts = True

    def run(self):
        text = "Check D1 LED on the LED PCB"
        text += "\n\nPASS = LED lit RED"
        text += "\nFAIL = LED is not lit"
        self.suite.set_text(text)
        
class ChargeBatteryStep1(Test):
    """Pogo power to battery board"""

    def run(self):
        # conditional to see whether TP5 and TP1 reads +5V (+/- 0.05V)
        text = "Detected +5.00V on battery board."
        text += "\n\nConfirm LED D5 is illuminated RED"
        text += "\nConfirm LEDs D2 and D4 are OFF completely"
        text += "\n\nIf D2 or D4 are illuminated at all, fail the test"

        self.suite.set_text(text)
        
class ChargeBatteryStep2(Test):
    """Measure pogo power voltage divider"""

    def run(self):
        # Conditional to measure TP1 and TP13 is below 4.5V
        self.suite.set_text("Measured 2.0V on voltage divider (TP1 and TP13\nMeasured 3.04V on battery PCB")

class TabletCharged(Test):
    """Check tablet charged"""

    def run(self):
        self.suite.form.msgbox("Action", "Turn off LOAD 1")
        self.suite.set_text("Observe LED D1 illuminated GREEN")

class BatteryBoardPowersTablet(Test):
    """Battery PCB and USB PCB Test"""

    def run(self):
        # Measure USB power between 
        pass

class FailTest(Test):
    """This test will automatically fail after 5 seconds"""

    def run(self):
        self.suite.set_text("This test will fail after 5 seconds")

        self.suite.form.update()
        time.sleep(5)

        self.suite.fail_test()