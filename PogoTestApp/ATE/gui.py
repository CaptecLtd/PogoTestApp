import tkinter as tk
import tkinter.constants as tkc
from tkinter import messagebox
from tkinter.messagebox import WARNING, ABORTRETRYIGNORE
from ATE.const import *
import os
#import tkmessagebox

class MainForm(tk.Frame):
    
    _reading_rows = None
    _stage_template = "Test Stage: {description}"
    _counting = False
    _count = 0
    _duration_template = "Test Duration: {seconds} Sec"

    # Methods to init and create the form

    def __init__(self, master):
        super().__init__(master)
        master.resizable(0,0) # Disallow resizing of the form
        master.geometry("800x480")
        master.title("X231 PCB Tester")

        self.root = master
        self.pack()
        self.create_widgets()

    def fullscreen(self, master, enable):
        master.attributes("-fullscreen", enable)

    def center(self, master):
        master.withdraw()
        master.update_idletasks()
        x = (master.winfo_screenwidth() - master.winfo_reqwidth()) / 2
        y = (master.winfo_screenheight() - master.winfo_reqheight()) / 2

        master.geometry("+%d+%d" % (x, y))
        master.deiconify()

    def create_widgets(self):
        padding = 10
        btn_font = "Arial 18 bold"
        header_font = "Arial 10 bold"

        self._duration_count = tk.StringVar()
        self._duration_count.set("Test Duration: N/A")

        current_row = 0

        # Test Stage information

        self.test_stage = tk.Label(self)
        self.test_stage["text"] = self._stage_template.format(description = "N/A")
        self.test_stage["font"] = "Arial 10 bold"
        self.test_stage.grid(column = 0, row = current_row, columnspan = 4, sticky = tkc.W + tkc.S, pady = 3)

        self.session_duration = tk.Label(self)
        self.session_duration["textvariable"] = self._duration_count
        self.session_duration["font"] = "Arial 10 bold"
        self.session_duration.grid(column = 3, row = current_row, sticky = tkc.E, columnspan = 2)

        # / Test Stage Information

        current_row =+ 1

        # Info text box container

        info_container = tk.Frame(self, width = 760, height = 180)
        info_container.grid(column = 0, row = current_row, columnspan = 5)
        info_container.columnconfigure(0, minsize = 760)
        info_container.rowconfigure(0, minsize = 180)

        # Member of info container
        self.info_label = tk.Label(info_container)
        self.info_label["text"] = "Ready. Press RESET to begin tests."
        self.info_label["bg"] = "white"
        self.info_label["fg"] = "black"
        self.info_label["bd"] = 1
        self.info_label["relief"] = "groove"
        self.info_label["anchor"] = tkc.NW
        self.info_label["wraplength"] = 740
        self.info_label["justify"] = tkc.LEFT
        self.info_label["font"] = ("Courier", 9)
        self.info_label.grid( pady = padding, columnspan = 6, column = 0, row = 0, sticky = tkc.W + tkc.E + tkc.N + tkc.S)
        # End info container

        current_row += 1

        # Readings container

        readings_container = tk.Frame(self, width = 760, height = 150)
        readings_container.grid(column = 0, row = current_row, columnspan = 5, sticky = tkc.W, pady = 5)

        # Readings headers

        h1 = tk.Label(readings_container)
        h1["text"] = "Voltage Measurements"
        h1["font"] = header_font
        h1.grid(column = 0, row = 0, columnspan = 2, sticky = tkc.W + tkc.N)

        h2 = tk.Label(readings_container)
        h2["text"] = "Digital Outputs"
        h2["font"] = header_font
        h2.grid(column = 2, row = 0, columnspan = 2, sticky = tkc.W + tkc.N)

        h3 = tk.Label(readings_container)
        h3["text"] = "Digital Inputs"
        h3["font"] = header_font
        h3.grid(column = 4, row = 0, columnspan = 2, sticky = tkc.W + tkc.N)

        # / Readings headers

        # Readings rows

        self._reading_rows = {
            "AD1": {"name": "AD1 Pogo Input Volts", "value": tk.StringVar(), "column": 0, "row": 1 },
            "AD2": {"name": "AD2 Tablet USB Volts", "value": tk.StringVar(), "column": 0, "row": 2 },
            "AD3": {"name": "AD3 Batt Board Power In Volts", "value": tk.StringVar(), "column": 0, "row": 3},
            "AD4": {"name": "AD4 Batt Board Temp Sense Cutoff", "value": tk.StringVar(), "column": 0, "row": 4},
            "AD5": {"name": "AD5 Batt Board Battery Volts", "value": tk.StringVar(), "column": 0, "row": 5},
            "AD6": {"name": "AD6 External USB Volts", "value": tk.StringVar(), "column": 0, "row": 6},
            "AD7": {"name": "AD7 Pogo Battery Output", "value": tk.StringVar(), "column": 0, "row": 7},

            "DOP1": {"name": "DOP1 Tablet Full Load Switch", "value": tk.StringVar(), "column": 2, "row": 1},
            "DOP2": {"name": "DOP2 Tablet Charged Load Switch", "value": tk.StringVar(), "column": 2, "row": 2},
            "DOP3": {"name": "DOP3 OTG Mode Trigger", "value": tk.StringVar(), "column": 2, "row": 3},
            "DOP4": {"name": "DOP4 D+ Ext USB", "value": tk.StringVar(), "column": 2, "row": 4},
            "DOP5": {"name": "DOP5 D- Ext USB", "value": tk.StringVar(), "column": 2, "row": 5},
            "DOP6": {"name": "DOP6 Tablet OTG Vout Activate", "value": tk.StringVar(), "column": 2, "row": 6},


            "DIP1": {"name": "DIP1 TP3 Q4 Startup Delay", "value": tk.StringVar(), "column": 4, "row": 1},
            "DIP2": {"name": "DIP2 Tablet OTG Sense", "value": tk.StringVar(), "column": 4, "row": 2},
            "DIP3": {"name": "DIP3 D+ Tablet USB Sense", "value": tk.StringVar(), "column": 4, "row": 3},
            "DIP4": {"name": "DIP4 D- Tablet USB Sense", "value": tk.StringVar(), "column": 4, "row": 4}
        }

        # Add all the configured rows to the form
        for itm in self._reading_rows.items():
            k = itm[0]
            v = itm[1]

            v["value"].set("...")

            lbl = tk.Label(readings_container)
            lbl["text"] = v["name"]
            lbl.grid(column = v["column"], row = v["row"], sticky = tkc.W + tkc.N)

            val = tk.Label(readings_container)
            val["textvariable"] = v["value"]
            val["width"] = 5
            val.grid(column = v["column"] + 1, row = v["row"], sticky = tkc.W + tkc.N, padx = 5)

        # / Reading rows
        # / Reading container

        current_row += 1

        # Control buttons

        self.pass_btn = tk.Button(self)
        self.pass_btn["text"] = "PASS"
        self.pass_btn["fg"] = "green"
        self.pass_btn["font"] = btn_font
        self.pass_btn.grid(padx = padding, pady = padding, sticky = tkc.W, column = 0, row = current_row)

        self.fail_btn = tk.Button(self)
        self.fail_btn["text"] = "FAIL"
        self.fail_btn["fg"] = "red"
        self.fail_btn["font"] = btn_font
        self.fail_btn.grid(padx = padding, pady = padding, column = 1, row = current_row)

        self.reset_btn = tk.Button(self)
        self.reset_btn["text"] = "RESET"
        self.reset_btn["font"] = btn_font
        self.reset_btn.grid(padx = padding, pady = padding, column = 2, row = current_row)

        self.abort_btn = tk.Button(self)
        self.abort_btn["text"] = "ABORT"
        self.abort_btn["font"] = btn_font
        self.abort_btn.grid(padx = padding, pady = padding, column = 3, row = current_row)

        self.shutdown_btn = tk.Button(self)
        self.shutdown_btn["text"] = "OFF"
        self.shutdown_btn["font"] = btn_font
        self.shutdown_btn["command"] = self.handle_shutdown
        self.shutdown_btn.grid(padx = padding, pady = padding, sticky = tkc.E, column = 4, row = current_row)

        # / Control buttons

    # / Form creation methods

    # Form control methods

    def set_info_pass(self):
        self.info_label["bg"] = "lightgreen"

    def set_info_fail(self):
        self.info_label["bg"] = "pink"

    def set_info_default(self):
        self.info_label["bg"] = "white"

    def set_text(self, text):
        "Sets the information text to the specified string"
        self.info_label["text"] = text
        self.update()

    def append_text_line(self, text):
        "Appends the specified text to the existing information string"
        self.info_label["text"] += "\n" + text
        self.update()

    def update_current_test(self, test):
        "Updates the test stage label with the details of the current test"
        self.test_stage["text"] = self._stage_template.format(description = test.description)

    def set_stage_text(self, text):
        self.test_stage["text"] = text

    def disable_all_buttons(self):
        self.disable_test_buttons();
        self.disable_control_buttons();

    def enable_all_buttons(self):
        self.enable_test_buttons();
        self.enable_control_buttons();

    def disable_test_buttons(self):
        "Disable pass and fail buttons"
        self.disable_pass_button();
        self.disable_fail_button();

    def enable_test_buttons(self):
        "Enable pass and fail buttons"
        self.enable_pass_button();
        self.enable_fail_button();

    def disable_control_buttons(self):
        self.disable_reset_button()
        self.disable_abort_button()

    def enable_control_buttons(self):
        self.enable_reset_button()
        self.enable_abort_button()

    def enable_reset_button(self):
        self.reset_btn["state"] = "normal"

    def disable_reset_button(self):
        self.reset_btn["state"] = "disabled"

    def enable_abort_button(self):
        self.abort_btn["state"] = "normal"

    def disable_abort_button(self):
        self.abort_btn["state"] = "disabled"

    def enable_pass_button(self):
        self.pass_btn["state"] = "normal"

    def enable_fail_button(self):
        self.fail_btn["state"] = "normal"

    def disable_pass_button(self):
        self.pass_btn["state"] = "disabled"

    def disable_fail_button(self):
        self.fail_btn["state"] = "disabled"

    def msgbox(self, title, text):
        messagebox.showinfo(title, text)

    def reset_dialogue(self):
        "Asks the user if they want to reset the current test"
        return messagebox.askyesno("RESET", "Do you want to re-run the current test?", icon = WARNING)

    def abort_dialogue(self):
        "Asks the user if they want to abort testing and reset the ATE"
        return messagebox.askyesno("ABORT", "Do you want to abort testing? This will finish the test session and show the summary.", icon = WARNING)

    def set_reading_value(self, key, value):
        self._reading_rows[key]["value"].set(value)

    def update_readings(self, voltages):

        for reading in voltages.items():
            self.set_reading_value(reading[0], reading[1])

    def handle_shutdown(self):
        if messagebox.askyesno("Shutdown?", "Are you sure you want to turn the ATE controller off?", icon = WARNING):
            if messagebox.askokcancel("Shutdown", "Shutdown will begin when you press OK.\n\nAfter the screen goes blank, please wait 15 seconds before cutting power."):
                if os.name == "posix":
                    os.system("/sbin/shutdown -h now")


    def update_duration(self):

        if self._counting:
            self._count += 1
            self._duration_count.set( self._duration_template.format(seconds = self._count))

        self.root.after(1000, self.update_duration)

    def reset_duration(self):
        self._count = 0

    def start_duration_count(self):
        self._counting = True

    def stop_duration_count(self):
        self._counting = False

    def clear_duration(self):
        self._duration_count.set("Test Duration: N/A")