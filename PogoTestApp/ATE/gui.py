import tkinter as tk
import tkinter.constants as tkc
from tkinter import messagebox
from tkinter.messagebox import WARNING, ABORTRETRYIGNORE
from ATE.const import *
import os
import os.path
import sys
import configparser
#import tkmessagebox

class MainForm(tk.Frame):
    
    reset_action = None
    abort_action = None
    selected_suite_index = None

    # Adds some primary colour goodness to backgrounds
    # for alignment debugging
    debug_backgrounds = False

    _reading_rows = None
    _stage_template = "Test Stage: {description}"
    _counting = False
    _count = 0
    _duration_template = "Test Duration: {seconds} Sec"

    # Methods to init and create the form

    def __init__(self, master):
        super().__init__(master)
        master.resizable(0,0) # Disallow resizing of the form
        if self.debug_backgrounds:
            master.configure(background='red')
        master.geometry("800x480")
        master.title("X231 PCB Tester")

        self.root = master
        if self.debug_backgrounds:
            self['bg'] = 'blue'
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
        padding = 8
        btn_font = "Arial 18 bold"
        header_font = "Arial 10 bold"

        self._duration_count = tk.StringVar()
        self._duration_count.set("Test Duration: N/A")

        # Build our popup menu
        self.popup = tk.Menu(self.root, tearoff = 0)
        self.popup.add_command(label = "RESET", command = self.handle_reset)
        self.popup.add_command(label = "ABORT", command = self.handle_abort)
        self.popup.add_separator()
        self.popup.add_command(label = "OFF", command = self.handle_shutdown)
        self.popup["font"] = btn_font

        self.bind("<Button-1>", self.handle_menu_hide)

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

        current_row += 1

        # Info text box container

        info_container = tk.Frame(self, width = 740, height = 80)
        info_container.grid(column = 0, row = current_row, columnspan = 8)
        info_container.columnconfigure(0, minsize = 740)
        info_container.rowconfigure(0, minsize = 80)

        # Member of info container
        self.info_label = tk.Text(info_container)
        self.info_label.images = []
        #self.info_label["text"] = "Ready. Press RESET to begin tests."
        self.info_label["bg"] = "white"
        self.info_label["fg"] = "black"
        self.info_label["bd"] = 1
        self.info_label["relief"] = "groove"
        #self.info_label["anchor"] = tkc.NW
        #self.info_label["wraplength"] = 740
        #self.info_label["justify"] = tkc.LEFT
        self.info_label["height"] = 9
        self.info_label["font"] = ("Courier", 11)
        self.info_label["wrap"] = tkc.WORD
        #self.info_label.pack(side = tkc.LEFT, fill = tkc.BOTH)
        self.info_label.grid(column = 0, row = 0, sticky = tkc.W + tkc.E + tkc.N + tkc.S)

        info_scroll = tk.Scrollbar(info_container)
        #info_scroll.pack(side = tkc.RIGHT, fill = tkc.Y)
        info_scroll.grid(column = 1, row = 0, sticky = tkc.N + tkc.S)
        info_scroll.config(command = self.info_label.yview)

        self.info_label.config(yscrollcommand = info_scroll.set)

        # End info container

        current_row += 1

        # Readings container

        readings_container = tk.Frame(self, width = 760, height = 150)
        readings_container.grid(column = 0, row = current_row, columnspan = 5, sticky = tkc.W, pady = 5)

        # Readings headers

        h1 = tk.Label(readings_container)
        h1["text"] = "Voltages (AD)"
        h1["font"] = header_font
        h1.grid(column = 0, row = 0, columnspan = 2, sticky = tkc.W + tkc.N)

        h2 = tk.Label(readings_container)
        h2["text"] = "Digital Outputs (DOP)"
        h2["font"] = header_font
        h2.grid(column = 2, row = 0, columnspan = 2, sticky = tkc.W + tkc.N)

        h3 = tk.Label(readings_container)
        h3["text"] = "Digital Inputs (DIP)"
        h3["font"] = header_font
        h3.grid(column = 6, row = 0, columnspan = 2, sticky = tkc.W + tkc.N)

        # / Readings headers

        # Readings rows

        self._reading_rows = {
            "AD1": {"name": "1 POGO", "value": tk.StringVar(), "column": 0, "row": 1 },
            "AD2": {"name": "2 +5V PWR", "value": tk.StringVar(), "column": 0, "row": 2 },
            "AD3": {"name": "3 IN", "value": tk.StringVar(), "column": 0, "row": 3},
            "AD4": {"name": "4 TP13 NTC", "value": tk.StringVar(), "column": 0, "row": 4},
            "AD5": {"name": "5 BAT", "value": tk.StringVar(), "column": 0, "row": 5},
            "AD6": {"name": "6 SENSE", "value": tk.StringVar(), "column": 0, "row": 6},
            "AD7": {"name": "7 SYS OUT", "value": tk.StringVar(), "column": 0, "row": 7},
            "AD8": {"name": "8 OUT", "value": tk.StringVar(), "column": 0, "row": 8},

            "DOP1": {"name": "1 Load ON", "value": tk.StringVar(), "column": 2, "row": 1},
            "DOP2": {"name": "2 Discharge Load", "value": tk.StringVar(), "column": 2, "row": 2},
            "DOP3": {"name": "3 TP7 GPIO", "value": tk.StringVar(), "column": 2, "row": 3},
            "DOP4": {"name": "4 TP5 GPIO", "value": tk.StringVar(), "column": 2, "row": 4},
            "DOP5": {"name": "5 TP6 GPIO", "value": tk.StringVar(), "column": 2, "row": 5},
            "DOP6": {"name": "6 T SW ON", "value": tk.StringVar(), "column": 2, "row": 6},
            "DOP7": {"name": "7 Cold sim", "value": tk.StringVar(), "column": 2, "row": 7},
            "DOP8": {"name": "8 Hot sim", "value": tk.StringVar(), "column": 2, "row": 8},
            "DOP9": {"name": "9 TO J7-1", "value": tk.StringVar(), "column": 4, "row": 1},
            "DOP10": {"name": "10 FLT loop back", "value": tk.StringVar(), "column": 4, "row": 2},
            "DOP11": {"name": "11 POGO ON GPIO", "value": tk.StringVar(), "column": 4, "row": 3},
            "DOP12": {"name": "12 BAT1 GPIO", "value": tk.StringVar(), "column": 4, "row": 4},
            "DOP13": {"name": "13 BAT0 GPIO", "value": tk.StringVar(), "column": 4, "row": 5},

            "DIP1": {"name": "1 TP3 Q4 Startup Delay", "value": tk.StringVar(), "column": 6, "row": 1},
            "DIP2": {"name": "2 Tabl OTG Sense", "value": tk.StringVar(), "column": 6, "row": 2},
            "DIP3": {"name": "3 D+ Tabl USB Sense", "value": tk.StringVar(), "column": 6, "row": 3},
            "DIP4": {"name": "4 D- Tabl USB Sense", "value": tk.StringVar(), "column": 6, "row": 4},
            "DIP5": {"name": "5 Tabl OTG Vout Act", "value": tk.StringVar(), "column": 6, "row": 5},
            "DIP6": {"name": "6 From J7-4", "value": tk.StringVar(), "column": 6, "row": 6},
            "DIP7": {"name": "7 J3 LINK OK", "value": tk.StringVar(), "column": 6, "row": 7},
            "DIP8": {"name": "8 LED RD", "value": tk.StringVar(), "column": 6, "row": 8},
            "DIP9": {"name": "9 LED GN", "value": tk.StringVar(), "column": 8, "row": 1},
            "DIP10": {"name": "10 USB PERpins OK", "value": tk.StringVar(), "column": 8, "row": 2},
            "DIP11": {"name": "11 +5V ATE in", "value": tk.StringVar(), "column": 8, "row": 3},
        }

        # Add all the configured rows to the form
        for itm in self._reading_rows.items():
            k = itm[0]
            v = itm[1]

            v["value"].set("...")

            lbl = tk.Label(readings_container)
            lbl["text"] = v["name"]
            #lbl["font"] = ("Arial Narrow", 10)
            lbl.grid(column = v["column"], row = v["row"], sticky = tkc.W + tkc.N)

            val = tk.Label(readings_container)
            val["textvariable"] = v["value"]
            val["width"] = 5
            val.grid(column = v["column"] + 1, row = v["row"], sticky = tkc.W + tkc.N)

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
        #self.reset_btn["text"] = "RESET"
        #self.reset_btn["font"] = btn_font
        #self.reset_btn.grid(padx = padding, pady = padding, column = 2, row = current_row)

        self.abort_btn = tk.Button(self)
        #self.abort_btn["text"] = "ABORT"
        #self.abort_btn["font"] = btn_font
        #self.abort_btn.grid(padx = padding, pady = padding, column = 3, row = current_row)

        self.menu_btn = tk.Button(self)
        self.menu_btn["text"] = "MENU"
        self.menu_btn["font"] = btn_font
        self.menu_btn["command"] = self.handle_menu
        self.menu_btn.grid(padx = padding, pady = padding, sticky = tkc.E, column = 4, row = current_row)

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
        self.info_label.images = []
        self.info_label["state"] = tkc.NORMAL
        self.info_label.delete(0.0, tkc.END)
        self.info_label.insert(tkc.END, text)
        self.info_label["state"] = tkc.DISABLED
        self.update()

    def clear_text(self):
        self.set_text("")

    def append_text_line(self, text):
        "Appends the specified text to the existing information string"
        self.info_label["state"] = tkc.NORMAL
        self.info_label.insert(tkc.END, "\n" + text)
        self.info_label["state"] = tkc.DISABLED
        self.update()

    def append_image(self, path):
        "Takes a path to a gif image and appends it on a new line to the info box."
        if os.path.exists(path):
            img = tk.PhotoImage(file = path)
            self.info_label.images.append(img)
            self.info_label["state"] = tkc.NORMAL
            self.info_label.insert(tkc.END, "\n")
            self.info_label.image_create(tkc.END, image = self.info_label.images[len(self.info_label.images) -1])
            self.info_label["state"] = tkc.DISABLED
        else:
            print("Image file ""%s"" not found" % path)

    def update_current_test(self, test):
        "Updates the test stage label with the details of the current test"
        self.test_stage["text"] = self._stage_template.format(description = test.description)

    def set_stage_text(self, text):
        self.test_stage["text"] = text

    def disable_all_buttons(self):
        self.disable_test_buttons()
        self.disable_control_buttons()

    def enable_all_buttons(self):
        self.enable_test_buttons()
        self.enable_control_buttons()

    def disable_test_buttons(self):
        "Disable pass and fail buttons"
        self.disable_pass_button()
        self.disable_fail_button()

    def enable_test_buttons(self):
        "Enable pass and fail buttons"
        self.enable_pass_button()
        self.enable_fail_button()

    def enable_test_buttons_delay(self, delay = 500):
        "Enable pass and fail buttons after 'delay' ms"
        self.root.after(delay, self.enable_test_buttons)

    def disable_control_buttons(self):
        self.disable_reset_button()
        self.disable_abort_button()

    def enable_control_buttons(self):
        self.enable_reset_button()
        self.enable_abort_button()

    def enable_reset_button(self):
        self.popup.entryconfig(0, state = "normal")

    def disable_reset_button(self):
        self.popup.entryconfig(0, state = "disabled")

    def enable_abort_button(self):
        self.popup.entryconfig(1, state = "normal")

    def disable_abort_button(self):
        self.popup.entryconfig(1, state = "disabled")

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

    def handle_abort(self):
        if self.abort_action != None:
            self.abort_action()

    def handle_reset(self):
        if self.reset_action != None:
            self.reset_action()

    def handle_menu(self):
        x, y = (self.menu_btn.winfo_rootx(), self.menu_btn.winfo_rooty() - self.popup.winfo_reqheight())
        self.popup.post(x, y)

    def handle_menu_hide(self, event):
        self.popup.unpost()

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


"""
This class is used to specify which suite of tests are to be run. It
modifies the tests.ini file's [settings] selected_suite key with the chosen index.
The PogoTestApp program then loads in the config and sets up the tests depending on the
suite chosen.

The classes specified in the ini file must exist (obviously).

This method was chosen as it's a little more modular and involves less modification to the 
main ATE software framework.

"""

class SuiteSelectionForm():

    def select_suite(self):
        elm = self.frm.suite_list.curselection()
        if len(elm) != 1:
            return

        self.config["settings"]["selected_suite"] = str(elm[0])
        with open("tests.ini", "w") as configfile:
            self.config.write(configfile)
            self.root.destroy()
            self.root.quit()

    def loop(self):
        self.root.mainloop()

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.root = tk.Tk()

        font = ("Arial", 20)

        self.config.read("tests.ini")

        # Create test suite selection window
        self.frm = tk.Toplevel(self.root)
        self.frm.title("Select test suite")
        self.frm.geometry("800x480")

        self.frm.lb = tk.Label(self.frm, text="Please select the test suite to run and tap BEGIN.")
        self.frm.lb["font"] = font
        self.frm.lb.pack()

        self.frm.suite_list = tk.Listbox(self.frm)
        self.frm.suite_list["font"] = font
        self.frm.suite_list["activestyle"] = "none"
        self.frm.suite_list.pack(fill=tk.BOTH, expand=1)
        self.frm.suite_list.selection_anchor(0)
        
        for k, v in self.config["suites"].items():
            self.frm.suite_list.insert(tk.END, v)

        self.frm.btn = tk.Button(self.frm, text="BEGIN", command=self.select_suite)
        self.frm.btn["font"] = font
        self.frm.btn.pack()

        self.frm.wm_attributes("-topmost", 1)

        