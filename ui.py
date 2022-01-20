from datetime import datetime

from tkinter import *
from tkinter.ttk import Combobox
from tkcalendar import DateEntry

from report import Report
from issa import *

FONT = ("Arial", 16, "normal")

class ISSAInterface:
    """User Interface for ISSA.
    
    Attributes:
        window
        att2
    """
    def __init__(self) -> None:
        now = datetime.now()
        self.window = Tk()
        self.window.title("iSSA")
        self.window.geometry('480x200')
        self.window.config(padx=20, pady=40)
        self.last_serial_number = self.get_last_serial_number()

        #Labels
        self.sn_label = Label(text="Serial Number", font=FONT)
        self.sn_label.grid(sticky=W, column=0, row=0)

        self.stauts_label = Label(text="", font=("Arial", 14))
        self.stauts_label.grid(sticky=W, column=0, row=3)
        
        # Input
        text = StringVar()
        text.set(self.last_serial_number)
        self.report_input = Entry(width=18, font=FONT, textvariable=text)
        self.report_input.grid(sticky=W, column=0, row=1)
        
        # Combobox
        options = StringVar() 
        self.options_box = Combobox(width=20, textvariable=options, font=FONT)
        self.options_box["values"] = ("Benchmark", "Log")
        self.options_box.current(0)
        self.options_box.grid(sticky=W, column=0, row=2, pady=10)
        
        # Button
        self.report_button = Button(
            width=12,
            height=3,
            text="Create Report",
            font=FONT,
            command=self.generate_report)
        self.report_button.grid(column=1, row=1, rowspan=2, padx=15)

        # Calendar
        # self.cal = DateEntry(bd=2)
        # self.cal.pack()

        self.window.mainloop()


    def get_last_serial_number(self) -> str:
        """
        Gets last serial number from Product Table.

        Returns
            serial_number (str): Latest product serial number.
        """
        product = ProductTable()
        return product.get_last_row()[0]

    
    def generate_report(self):
        report = Report()
        serial_number = self.report_input.get()
        selected_option = self.options_box.get()
        
        if selected_option.lower() == "benchmark":
            if serial_number:
                report.write_product_benchmark(serial_number)
                self.stauts_label.config(text="Benchmark successfully created!")
            else:
                report.write_last_product_benchmark()
        
        elif selected_option.lower() == "log":
            if serial_number:
                report.write_log_test(serial_number)
                self.stauts_label.config(text="Log successfully created!")
            else:
                report.write_log_test_last_product()
