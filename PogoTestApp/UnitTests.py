"""
FunctionTests

Script to test functionality of the pogolib.input module without running through the application.
This script is designed to run without the ADC libraries and so uses the simulation features of the Channel class.
"""

import unittest
import time
from math import ceil

from ATE.tests import TestProcedure
from ATE.suite import TestSuite
from ATE.adc import Channel

class TestVoltageMethods(unittest.TestCase):

    def setUp(self):
        # Set voltage inside each test case, initialises to 0.0
        self.channel = Channel(1)
        # Force the channel to simulation mode so we're not attempting to read actual voltages from the ADC.
        self.channel.set_simulation_mode(True)

    def tearDown(self):
        self.channel = None

    def test_read(self):
        self.assertEqual(0.0, self.channel.read_voltage())
        self.channel.set_simulation_voltage(5.0)
        self.assertEqual(5.0, self.channel.read_voltage())

    def test_near(self):
        self.channel.set_simulation_voltage(5.0)
        self.assertTrue(self.channel.voltage_near(5.0, 0.0))

        self.channel.set_simulation_voltage(4.99)
        self.assertTrue(self.channel.voltage_near(5.0, 0.01))
        self.channel.set_simulation_voltage(5.01)
        self.assertTrue(self.channel.voltage_near(5.0, 0.01))

        self.channel.set_simulation_voltage(4.98)
        self.assertTrue(self.channel.voltage_near(5.0, 0.01))

        self.assertFalse(self.channel.voltage_near(5.0, 0.001))

        self.channel.set_simulation_voltage(4.94)
        self.assertFalse(self.channel.voltage_near(5.0, 0.01))

    def test_between(self):
        self.channel.set_simulation_voltage(5.0)
        self.assertTrue(self.channel.voltage_between(4.99, 5.01, 0.0))

        self.assertFalse(self.channel.voltage_between(5.1, 5.2, 0.0))

        self.channel.set_simulation_voltage(0.0)
        self.assertFalse(self.channel.voltage_between(4.95, 5.05, 0.01))

    def test_zero(self):
        self.channel.set_simulation_voltage(0.0)
        self.assertTrue(self.channel.zero_voltage())

    def test_await(self):
        self.channel.set_simulation_voltage(0.0)
        self.assertTrue(self.channel.await_voltage(0.0, 0.0))

        time_before = time.time()
        self.assertFalse(self.channel.await_voltage(1.0, 0.0, 1))

        self.assertGreaterEqual(ceil(time.time()), ceil(time_before + 1))

    def test_read_voltage_range(self):
        self.channel.set_simulation_voltage(5.0)

        voltage, valid, readings = self.channel.read_voltage_range(5)
        self.assertTrue(valid)


class TestFunctionTests(unittest.TestCase):

    def test_base_procedure(self):
        proc = TestProcedure()

        self.assertEqual("not_run", proc.state)
        self.assertEqual("Not Run", proc.format_state())

        proc.set_passed()

        self.assertEqual("passed", proc.state)
        self.assertEqual("Passed", proc.format_state())

        proc.set_failed()

        self.assertEqual("failed", proc.state)
        self.assertEqual("FAILED", proc.format_state())

        proc.reset()

        self.assertEqual("not_run", proc.state)
        self.assertEqual("Not Run", proc.format_state())


class TestSuitePassOperation(unittest.TestCase):

    def test_testsuite(self):

        suite = TestSuite()
        suite.add_test(TestProcedure())
        suite.add_test(TestProcedure())

        suite.reset()

        suite.pass_test()

        self.assertEqual("passed", suite.tests[0].state)

        suite.pass_test()

        self.assertEqual("passed", suite.tests[1].state)

if __name__ == '__main__':
    unittest.main()
