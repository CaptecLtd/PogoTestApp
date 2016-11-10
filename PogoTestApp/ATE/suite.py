from enum import Enum
from ATE.adc import Channel
from ATE.gui import MainForm
import ATE.digio as digio

class TestSuite(object):
    "Suite of tests for the user to complete. Controls the running and state of tests. Call TestSuite.reset() before interacting with any tests. "
    tests = []
    current_test = -1
    form = None

    def execute(self):
        "Processes any GUI updates and runs the current test's setUp() and run() methods"

        # GUI isn't created when running Unit Tests so we check here before doing GUI operations.
        if self.form:
            self.form.set_info_default()
            self.form.enable_control_buttons()
            self.form.enable_test_buttons()
            self.form.update_current_test(self.tests[self.current_test])

        self.tests[self.current_test].breakout = False
        self.tests[self.current_test].setUp()
        self.tests[self.current_test].run()

    def add_test(self, test):
        test.suite = self
        self.tests.append(test)

    def set_text(self, text):
        self.form.info_label["text"] = text

    def append_text(self, text):
        self.form.info_label["text"] += "\n" + text

    def pass_test(self):
        "Sets the current test as passed and advances to the next test"
        self.tests[self.current_test].set_passed()
        self.advance_test()

    def fail_test(self):
        "Sets the current test as failed. If the test aborts, summary is shown. If not, advances to the next test"
        self.tests[self.current_test].set_failed()
        if self.tests[self.current_test].aborts:
            self.summary()
        else:
            self.advance_test()

    def abort(self):
        "Asks the user if they want to abort testing and return to the beginning and processes the answer."
        if self.form.abort_dialogue():
            self.form.disable_test_buttons()
            self.summary()
            self.current_test = -1

    def reset(self):
        "Asks the user if they want to start the current test again and processes the answer."

        # If we've just loaded up, use the RESET button to initialise testing
        if self.current_test == -1:
            # Set up the digital I/O pins in case they've changed through previous tests.
            digio.setup()

            # Reset any previous test results
            self.reset_test_results()

            # Kick off the first test
            self.current_test = 0
            self.execute()
            return

        if self.form.reset_dialogue():
            self.execute()

    def reset_test_results(self):
        for test in self.tests:
            test.reset()

    def advance_test(self):
        "If tests are remaining in the queue, runs the current test's tearDown() method and advances to the next test. If no tests are remaining, shows summary"

        # Check to see if we've got more groups to run. If we don't, show the summary.
        if self.current_test >= len(self.tests) -1:
            # If our form is declared, run the summary method. If not, we're likely running from unit tests so ignore.
            if self.form:
                self.summary()
        else:
            # If we do have more tests, clean up the current test, advance the current test variable and execute the test.
            self.tests[self.current_test].tearDown()
            self.current_test += 1
            self.execute()

    def summary(self):
        "Writes a summary of the loaded tests and their results"
        self.current_test = -1
        self.form.disable_abort_button()
        self.form.set_stage_text("Testing Ended.")

        results = "Test suite completed."
        failures = []
        passes = []
        not_run = []
        run_tests = []

        for test in self.tests:

            if test.state == "failed":
                failures.append(test)
                run_tests.append(test)
            if test.state == "passed":
                passes.append(test)
                run_tests.append(test)

            if test.state == "not_run":
                not_run.append(test)

        results += " {}/{} tests were run, of which {} passed and {} failed.".format(len(run_tests), len(self.tests), len(passes), len(failures))

        if len(failures) > 0:
            results += "\n\nFailures:\n"

        for test in failures:
            results += test.description + "\n"
            for failure in test.failure_log:
                results += "    " + failure + "\n"

        if len(failures) > 0:
            self.form.set_info_fail()
        elif len(failures) == 0 and len(passes) > 0:
            self.form.set_info_pass()

        self.set_text(results)
        self.form.disable_test_buttons()
