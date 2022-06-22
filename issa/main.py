from random import randint
# from data.temp import logs
from issa import *
from rf_bands import LTE, WCMDA, GSM


def init_database():
    product_table = ProductTable()
    log_table = LogTable()
    rf_table = BandTable()
    prf_table = ProductBandTable()
    benchmark_table = BenchmarkTable()
    pb_table = ProductBenchmarkTable()
    test_table = TestTable()
    pt = ProductTestTable()
    
    prf_table.drop()
    pb_table.drop()
    log_table.drop()
    rf_table.drop()
    benchmark_table.drop()
    product_table.drop()
    pt.drop()
    test_table.drop()

    product_table.create()
    log_table.create()
    rf_table.create()
    prf_table.create()
    benchmark_table.create()
    pb_table.create()
    test_table.create()
    pt.create()


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
    logs = False
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

    bands = LTE + WCMDA + GSM
    insert_fake_data(table_name="Band", table_values=bands)
    
    measurements = []
    for serial_number in serial_numbers:        
        measurement = {
            'serial_number': serial_number,
            'frequency': bands[randint(0, 3)]['frequency'],
            'power': 23,
            'units': 'dBm'
        }        
        measurements.append(measurement)

    insert_fake_data(table_name="Product_Band", table_values=measurements)

    tests = [
        {"name": "test 1", "type": "text", "min_limit": "te", "max_limit": "", "units": ""},
        {"name": "test 2", "type": "numeric", "min_limit": "1", "max_limit": "3", "units": "volts"},
        {"name": "test 3", "type": "numeric", "min_limit": "4", "max_limit": "-7", "units": "ohms"},
        {"name": "did f1", "type": "text", "min_limit": "ABC", "max_limit": "", "units": "DID F1"},
        {"name": "did f2", "type": "text", "min_limit": "FGT", "max_limit": "", "units": ""},
    ]
    insert_fake_data(table_name="Test", table_values=tests)

    for serial_number in serial_numbers:
        for index, test in enumerate(tests):
            result = str(randint(0, 10)) if test["type"] == "numeric" else "blabla"
            insert_fake_data(table_name="Product_Test", table_values=[{"serial_number": serial_number, "test_id": index + 1, "result": result}])


if "__main__" == __name__:
    init_database()

    populate_db()

    # #Create log test report
    # serial_number = "T21000000101"
    # report = Report()
    # report.write_product_benchmark(serial_number)
    # report.write_last_product_benchmark()
    # report.write_log_test_last_product()