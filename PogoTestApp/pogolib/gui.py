import tkinter as tk
import tkinter.constants as tkc
from tkinter import messagebox
#import tkmessagebox

class MainForm(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)
        master.resizable(0,0)
        master.geometry("800x480")
        master.title("X231 PCB Tester")
        self.pack()
        self.create_widgets()

    def set_text(self, text):
        self.info_label["text"] = text

    def create_widgets(self):
        padding = 10
        btn_font = ("Arial", 18, "bold")

        info_container = tk.Frame(self, width = 760, height = 400)
        info_container.grid(column = 0, row = 0, columnspan = 3)
        info_container.columnconfigure(0, minsize = 760)
        info_container.rowconfigure(0, minsize = 400)

        self.info_label = tk.Label(info_container)
        self.info_label["text"] = "Ready. Press RESET to begin tests."
        #self.info_label["width"] = 85
        #self.info_label["height"] = 21
        self.info_label["bg"] = "darkblue"
        self.info_label["fg"] = "white"
        self.info_label["bd"] = 1
        self.info_label["relief"] = "groove"
        self.info_label["anchor"] = tkc.NW
        self.info_label["wraplength"] = 740
        self.info_label["justify"] = tkc.LEFT
        self.info_label["font"] = ("Arial", 12)
        self.info_label.grid(padx = padding, pady = padding, columnspan = 3, column = 0, row = 0, sticky = tkc.W + tkc.E + tkc.N + tkc.S)
        #self.info_label.grid()
        #self.info_label.columnconfigure(0, minsize = 500)

        
        self.pass_btn = tk.Button(self)
        self.pass_btn["text"] = "PASS"
        self.pass_btn["fg"] = "green"
        self.pass_btn["font"] = btn_font
        self.pass_btn.grid(padx = padding, pady = padding, sticky = tkc.W, column = 0, row= 1)

        self.reset_btn = tk.Button(self)
        self.reset_btn["text"] = "RESET"
        self.reset_btn["font"] = btn_font
        self.reset_btn.grid(padx = padding, pady = padding, column = 1, row= 1)

        self.fail_btn = tk.Button(self)
        self.fail_btn["text"] = "FAIL"
        self.fail_btn["fg"] = "red"
        self.fail_btn["font"] = btn_font
        self.fail_btn.grid(padx = padding, pady = padding, sticky = tkc.E, column = 2, row = 1)

    def disable_test_buttons(self):
        self.disable_pass_button();
        self.disable_fail_button();

    def enable_test_buttons(self):
        self.enable_pass_button();
        self.enable_fail_button();

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
