#!/usr/bin/python

from pogolib import gui, suite, tests
import tkinter as tk

root = tk.Tk()
main_frm = gui.MainForm(root)

test_suite = suite.TestSuite()
test_suite.form = main_frm

test_suite.form.pass_btn["command"] = test_suite.pass_test
test_suite.form.fail_btn["command"] = test_suite.fail_test
test_suite.form.reset_btn["command"] = test_suite.reset

test_suite.add_test(tests.MeasurePowerOnDelay())
test_suite.add_test(tests.PogoPowerInput())
test_suite.add_test(tests.ChargeBatteryStep1())
test_suite.add_test(tests.ChargeBatteryStep2())
test_suite.add_test(tests.TabletCharged())
# test_suite.add_test(tests.FailTest())

main_frm.disable_test_buttons()

root.mainloop()
