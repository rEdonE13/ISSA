import os
import pandas as pd
from datetime import datetime

from issa import *

#TODO (redone13): Ask user from_date and to_date
from_date = datetime(2021, 12, 20)
to_date = datetime.now().date()


#TODO (redone13): Ask user for a product_type
product_type = "2906-100-557-51"

class Report:
    #TODO (redone13): Add documentation
    def __init__(self) -> None:
        self.base_path = self.create_base_path()
        self.log_test_path = self.base_path + "/LogTest.xlsx"
        self.benchmark_path = self.base_path + "/Benchmark.xlsx"


    def create_base_path(self) -> str:
        """
        """
        base_path = "../reports"
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        return base_path


    def write_product_benchmark(self, serial_number: str) -> None:
        #TODO (redone13): Add serial number to the begining of the file name
        #     and current date yymmdd
        #     SerialNumber_ReportName_YYMMDD.xlsx
        product = ProductTable()
        if product.is_valid(serial_number):
            pb = ProductBenchmarkTable()
            data = pb.get_product_benchmark(serial_number)
            cols = ['Serial Number', 'Test Step', 'Duration in sec', 'Date']
            with pd.ExcelWriter(self.benchmark_path) as writer:
                df = pd.DataFrame(data, columns=cols)
                df.to_excel(writer, sheet_name=serial_number, index=False)
        else:
            print("product not found!")


    def write_last_product_benchmark(self) -> None:
        """Writes a report from the last serial number in the db."""
        product = ProductTable()
        last_row = product.get_last_row()
        last_sn = last_row[0]
        self.write_product_benchmark(last_sn)
    

    def write_log_test(self, serial_number: str) -> None:
        """
        Writes a report log from the provided serial number.
        
        Parameters: 
            serial_number (str): Serial Number
        """
        log = LogTable()
        logs = log.get_logs_by_serial_number(serial_number)
        with pd.ExcelWriter(self.log_test_path) as writer:
            df = pd.DataFrame(logs, columns=['Serial Number', 'Type', 'Description', 'Creation Date'])
            df.to_excel(writer, sheet_name=serial_number, index=False)


    def write_log_test_last_product(self) -> None:
        """Writes a report log from the last serial number."""
        product = ProductTable()
        last_row = product.get_last_row()
        last_sn = last_row[0]
        self.write_log_test(last_sn)


    #TODO (redone13): Implement a function for writing a benchmark report based on the product type.

    #TODO (redone13): Implement a function for writing a test log report based on the product type.

    #TODO (redone13): Add beautification to generated Excel Reports.