"""
X231 PCBA Automatic Test Equipment Control Software
Copyright (c) 2016 Captec Ltd

"""

try:

    # Import our modules
    from ATE import gui, tests, suite, const, version, adc, digio
    import sys
    import tkinter as tk
    import configparser
    import importlib
    from threading import Thread
    from getopt import getopt, GetoptError
    from time import sleep

    suite_selection = gui.SuiteSelectionForm()
    suite_selection.loop()

    # Create our Tk instance for the form
    root = tk.Tk()
    main_frm = gui.MainForm(root)

    # Create our test suite instance and link to the form
    test_suite = suite.TestSuite()
    test_suite.form = main_frm

    # Link the pass/fail/reset buttons to their actions
    test_suite.form.pass_btn["command"] = test_suite.pass_test
    test_suite.form.fail_btn["command"] = test_suite.fail_test
    test_suite.form.reset_action = test_suite.reset
    test_suite.form.abort_action = test_suite.abort

    #test_suite.add_test(tests.TestXX_FakeTest())

    config = configparser.ConfigParser()
    config.read("tests.ini")
    suite_idx = config["settings"]["selected_suite"]

    for idx, cls in config["suite%d" % int(suite_idx)].items():
        test_suite.add_test(getattr(tests, cls))

    test_suite.add_test(tests.TestEnd_TestsCompleted())

    # Disable input buttons to start with
    main_frm.disable_all_buttons()

    # Process command args.
    # -f = expand GUI to full screen
    #     (This is used on the Raspberry Pi)
    opts, args = getopt(sys.argv, "f")

    if args.count("-f") != 0:
        main_frm.fullscreen(root, True)

    # Set up our digital I/O before using it.
    digio.setup()

    # Update all readings (A/D and GPIO I/O each second)
    def update_readings():
        readings = adc.read_all_voltages()
        readings.update(digio.read_all_inputs())
        readings.update(digio.read_all_outputs())
        main_frm.update_readings(readings)
        root.after(1000, update_readings)

    # Attempt to set "OK" on each label.
    def readings_display_test():
        main_frm.set_text("Initialising readings")
        readings = adc.read_all_voltages()
        readings.update(digio.read_all_inputs())
        readings.update(digio.read_all_outputs())

        for reading in readings.items():
            main_frm.set_reading_value(reading[0], "OK")
            main_frm.update()
            sleep(0.1)

        main_frm.enable_reset_button()

    # Channel conversion factor times the impedence conversion
    # Circuit impedence compensation = 1.1505
    # Voltage divider compensation = 1.575
    adc.global_conversion_factor = (1.1505 * 1.575)

    # Different conversion factor for AD4.
    adc.conversion_factors = {
        const.AD4_V_TP13_NTC: 1.1505 * 0.8710
        }

    # Kick off the readings display test
    readings_display_test()

    # Kick off the reading updates.
    update_readings_thread = Thread(target = update_readings)
    update_readings_thread.start()

    # Kick off the test duration update thread.
    update_duration_thread = Thread(target = test_suite.form.update_duration)
    update_duration_thread.start()

    # Make the suite ready and display the intro text.
    test_suite.ready()

    # Process GUI events.
    root.mainloop()

# Handle all exceptions with a print to the console and a message box
except:
    import traceback
    from tkinter import messagebox
    exception = traceback.format_exc()
    print(exception)
    messagebox.showerror("Error", exception)
finally:
    sys.exit()