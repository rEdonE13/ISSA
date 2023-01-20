"""Report Generation"""

import os
import pandas as pd

from issa import ProductTable, ProductBenchmarkTable, LogTable


class Report:
    """
    A class to represent a Report.

    Attributes:
        base_path           (str): Base report path
        log_test_path       (str): Log report path
        benchmark_path      (str): Benchmark report path
        dids_report_path    (str): DIDs report path

    Methods:
        create_base_path():
            Set base path for all report files.    
    """
    def __init__(self) -> None:
        self.base_path          = self.create_base_path()
        self.log_test_path      = self.base_path + "/LogTest.xlsx"
        self.benchmark_path     = self.base_path + "/Benchmark.xlsx"
        self.dids_report_path   = self.base_path + "/DIDs_Report.xlsx"


    def create_base_path(self) -> str:
        """
        Set base path for all report files.
        """
        base_path = "reports"
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        return base_path


    def write_product_benchmark(self, serial_number: str) -> None:
        """
        Generates a benchmark report realeted to an specific product.

        Parameters
            serial_number (str): Serial number

        Returns
            None
        """
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

        Parameters
            serial_number (str): Serial Number

        Returns
            None
        """
        log = LogTable()
        logs = log.get_logs_by_serial_number(serial_number)
        with pd.ExcelWriter(self.log_test_path) as writer:
            df = pd.DataFrame(  logs,
                                columns=['Serial Number', 'Type', 'Description', 'Creation Date'])
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

    #TODO (redone13): Create a DID Report.
    def write_dids_report(self, serial_number) -> None:
        """
        Writes a DID reports for variants liberation.

        Parameters
            serial_number   (str):  Serial Number

        Returns
            None
        """
        product = ProductTable()
        test_dids = product.get_product_dids(serial_number)
        with pd.ExcelWriter(self.dids_report_path) as writer:
            df = pd.DataFrame(test_dids, columns=['Test Name', 'Min Limit', 'Max Limit', 'Units'])
            df.to_excel(writer, sheet_name=serial_number, index=False)
