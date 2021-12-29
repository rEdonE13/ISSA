from issa import *
from random import randint
from report import Report
from data.temp import logs
from ui import *


def init_database():
    product_table = ProductTable()
    log_table = LogTable()
    rf_table = RFTechTable()
    prf_table = ProductRFTechTable()
    benchmark_table = BenchmarkTable()
    pb_table = ProductBenchmarkTable()
    
    prf_table.drop()
    pb_table.drop()
    log_table.drop()
    rf_table.drop()
    benchmark_table.drop()
    product_table.drop()

    product_table.create()
    log_table.create()
    rf_table.create()
    prf_table.create()
    benchmark_table.create()
    pb_table.create()


def insert_fake_data(table_name: str, table_values: list):
    table = ISSA()
    data = {
        "table_name": table_name,
        "table_values": table_values
    }

    table.insert(data)


def populate_db():
    global logs
    serial_numbers = [f"T{21000000100 + i}" for i in range(10)]
    benchmarks = [f"test {1 + i}" for i in range(30)]
    logs = logs if logs else [f"log {i + 1}" for i in range(10)]
    
    #Insert product
    for serial_number in serial_numbers:
        product = {"serial_number": serial_number, "desc": "Model S", "type": "2021-100-002-00"}
        insert_fake_data(table_name="Product", table_values=[product])
    #Insert logs
        data =[]
        for log in logs:
            data.append({"type": "verbose", "desc": log, "serial_number": serial_number})
        insert_fake_data(table_name="Log", table_values=data)
    #Insert product benchmarks
        for i, benchmark in enumerate(benchmarks):
            pb = {"serial_number": serial_number, "benchmark_id": i+1, "duration_sec": randint(1,20)}
            insert_fake_data(table_name="Benchmark", table_values=[{"name": benchmark}])
            insert_fake_data(table_name="Product_Benchmark", table_values=[pb])


if "__main__" == __name__:
    issa_ui = ISSAInterface()

    # init_database()

    # populate_db()

    # #Create log test report
    # serial_number = "T21000000101"
    # report = Report()
    # report.write_product_benchmark(serial_number)
    # report.write_last_product_benchmark()
    # report.write_log_test_last_product()