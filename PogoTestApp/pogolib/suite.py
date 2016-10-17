from enum import Enum

class TestSuite(object):
    """Suite of tests for the user to complete. Contains instances of Test"""
    tests = []
    current_test = 0
    form = object

    def execute(self):
        self.form.enable_test_buttons()
        self.tests[self.current_test].run()

    def add_test(self, test):
        test.suite = self
        self.tests.append(test)

    def set_text(self, text):
        self.form.info_label["text"] = text

    def pass_test(self):
        self.tests[self.current_test].set_passed()
        self.advance_test()

    def fail_test(self):
        self.tests[self.current_test].set_failed()
        self.summary()

    def reset(self):
        self.form.info_label["bg"] = "darkblue"
        self.reset_test_results()
        self.current_test = 0
        self.execute()

    def reset_test_results(self):
        for test in self.tests:
            test.reset()

    def advance_test(self):

        # Check to see if we've got more groups to run
        if self.current_test >= len(self.tests) -1:
            self.summary()
        else:
            self.current_test += 1
            self.execute()

    def summary(self):
        results = "Test suite completed. Results:\n\n"
        tests = len(self.tests)
        failures = 0
        passes = 0

        for test in self.tests:
            results += "{0}: {1}\n".format(test.__doc__, self.format_state(test.state))
            if test.state == TestState.failed:
                failures += 1
            if test.state == TestState.passed:
                passes += 1

        results += "\n\nTests: {}, Passes: {}, Failures: {}".format(tests, passes, failures)

        if failures >= 0:
            self.form.info_label["bg"] = "darkred"

        if failures == 0:
            self.form.info_label["bg"] = "darkgreen"

        self.set_text(results)
        self.form.disable_test_buttons()

    def format_state(self, state):
        return {
            TestState.passed: "Passed",
            TestState.failed: "FAILED",
            TestState.not_run: "Not Run"
        }.get(state, "Unknown")

class TestState(Enum):
    not_run = 1
    passed = 2
    failed = 3