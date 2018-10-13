from enum import Enum
from threading import Thread
from ATE.adc import Channel
from ATE.gui import MainForm
import ATE.digio as digio
import ATE.const as const
import ATE.version as version

class TestSuite(object):
    "Suite of tests for the user to complete. Controls the running and state of tests. Call TestSuite.reset() before interacting with any tests. "
    tests = []
    current_test = -1
    selected_suite = None
    form = None
    timer = None
    summary_shown = False

    def ready(self):
        "Instructs the suite to show the intro text and await operator input."
        self.form.set_info_default()
        self.current_test = -1
        self.form.set_text(const.INTRO_TEXT.format(hwrevision = version.HARDWARE_REVISION, swrevision = version.SOFTWARE_REVISION, swdate = version.SOFTWARE_RELEASE_DATE))
        self.form.set_stage_text("Test Stage: N/A")
        self.form.reset_duration()
        self.form.disable_abort_button()
        self.form.disable_test_buttons()
        self.form.clear_duration()

    def execute(self):
        "Processes any GUI updates for the current test and runs the current test's setUp() and run() methods in a thread"

        thread = Thread(target = self._execute)
        thread.start()

    def _execute(self):
        "Thread worker for running GUI updates, executing the test and potentially advancing to the next test."
        
        # GUI isn't created when running Unit Tests so we check here before doing GUI operations.
        if self.form:
            self.form.set_info_default()
            self.form.enable_control_buttons()
            self.form.update_current_test(self.tests[self.current_test])

            # We enable pass/fail buttons automatically after a delay if the test allows it and it's not going to auto advance on pass.
            if self.tests[self.current_test].enable_pass_fail and not self.tests[self.current_test].auto_advance:
                self.form.enable_test_buttons_delay()
            else:
                self.form.disable_test_buttons()

        self.tests[self.current_test].breakout = False
        self.tests[self.current_test].setUp()
        self.tests[self.current_test].run()

        # If the current test is set to advance on pass and it has passed, advance it!
        if self.tests[self.current_test].state == "passed" and self.tests[self.current_test].auto_advance:
            self.form.set_info_pass()
            self.advance_test()

    def add_test(self, test):
        "Adds an instance of tests.TestProcedure to the list of tests to run"
        test.suite = self
        self.tests.append(test)

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
            self.form.stop_duration_count()
            self.summary()

    def reset(self):
        "Asks the user if they want to start the current test again and processes the answer."

        # If we've just finished a testing cycle (summary shown), show the intro text again.
        if self.summary_shown:
            self.summary_shown = False
            self.ready()
            return 

        # If we've just loaded up after self.ready(), use the RESET button to initialise testing
        if self.current_test == -1:
            # Set up the digital I/O pins in case they've changed through previous tests.
            digio.setup()

            if self.form:
                self.form.reset_duration()
                self.form.start_duration_count()

            # Reset any previous test results
            self.reset_test_results()

            # Kick off the first test
            self.current_test = 0
            self.execute()
            return

        # If we're in the middle of a test, ask the user if they want to start this test again and do so if true.
        if self.form.reset_dialogue():
            self.execute()

    def reset_test_results(self):
        "Loops through all the configured tests and calls the TestProcedure class' reset() method"
        for test in self.tests:
            test.reset()

    def advance_test(self):
        "If tests are remaining in the queue, runs the current test's tearDown() method and advances to the next test. If no tests are remaining, shows summary"

        # Check to see if we've got more groups to run. If we don't, show the summary.
        if self.current_test >= len(self.tests) -1:
            
            self.form.stop_duration_count()
            # If our form is declared, run the summary method. If not, we're likely running from unit tests so ignore.
            if self.form:
                self.summary()

        else:
            # If we do have more tests, clean up the current test, advance the current test variable and execute the test.
            self.tests[self.current_test].wait(3)
            self.tests[self.current_test].tearDown()
            self.current_test += 1
            self.form.clear_text()
            self.execute()

    def summary(self):
        "Writes a summary of the loaded tests and their results"
        #self.current_test = -1
        self.form.disable_abort_button()
        self.form.set_stage_text("Testing Ended.")

        # Reset digital I/O back to defaults
        digio.setup()

        results = "Test suite completed in {} seconds.".format(self.form._count)
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

        self.form.set_text(results)
        self.form.disable_test_buttons()
        self.summary_shown = True

