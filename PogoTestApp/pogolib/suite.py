

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
        self.current_test = 0
        self.execute()

    def advance_test(self):

        # Check to see if we've got more groups to run
        if self.current_test >= len(self.tests) -1:
            self.summary()
        else:
            self.current_test += 1
            self.execute()

    def summary(self):
        results = "Test suite completed. Results:\n\n"

        for test in self.tests:
            results += "{0}: {1}\n".format(test.__doc__, test.state)

        self.set_text(results)
        self.form.disable_test_buttons()