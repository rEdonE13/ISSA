"""Intelligent Storage System Application."""

import os
import sqlite3
from sqlite3 import Connection, Error
from sqlite3.dbapi2 import IntegrityError


class ISSA:
    """
    A class to represent the Intelligent Storage System Administration.

    Attributes:
        db_file     (str): Path to the SQLite DB.
        table_name  (str): Name of the DB table for a child class.
        primary_key (str): Name of the DB table primary key.

    Methods:
        create_connection():
            definition
        create(create_table_sql):
            Executes the provided SQL script to create a table
        drop():
            Drops the DB table from the calling subclass.
        insert():
            Insert data into the database.
        fetch():
            Fetches all data from the input query.
        get_last_row():
            Gets the last row of the calling child class.
        is_valid():
            Looks if the pk_value exists in the calling child class DB table_name.
    """
    def __init__(self, db_file: str = "C:/Pruef/Sqlite/db/pme.db") -> None:
        self.db_file = db_file
        self.cwd = os.getcwd()
        self.table_name = ""
        self.primary_key = "id"
        self.create_connection()


    def create_connection(self) -> Connection:
        """
        Create a db connection

        Returns
            conn (obj): sqlite3 connection obj
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as err:
            print(err)
            return None


    def create(self, create_table_sql: str) -> None:
        """
        Executes the provided SQL script to create a table.

        Parameters
            create_table_sql (str): SQL script

        Returns
            None
        """
        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                cur.executescript(create_table_sql)
        except Error as err:
            print(err)


    def drop(self) -> None:
        """
        Drops the DB table from the calling subclass.

        If a subclass provide a table_name, this function will drop it.

        Parameters
            None

        Returns
            None
        """
        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"DROP TABLE IF EXISTS {self.table_name};")
        except Error as err:
            print(err)


    def insert(self, table_data) -> None:
        """
        Inserts data into the db.

        Parameters
            table_data  (dict): dict containing the table name and values to insert.

        Returns
            None

        Raises
            IntegrityError: Let the error by pass.
        """
        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                for item in table_data["table_values"]:
                    cols = tuple(item.keys()) if len(item.keys()) > 1 else str(tuple(item.keys())).replace(",", "")
                    values = ('?,'*len(item)).rstrip(",")
                    query=f"INSERT INTO {table_data['table_name']} {cols} VALUES ({values})"
                    params = tuple(item.values())
                    cur.execute(query, params)
                conn.commit()
        except IntegrityError:
            pass
        except Error as err:
            print(err)


    def insert_values(self, columns: list, table_data: list) -> None:
        """
        Inserts data from the provided params from TestStand.

        Parameters
            columns     (list): Column names of the DB table.
            table_data  (list): Values for the provided columns.

        Returns
            None
        """

        columns = columns or []
        table_data = table_data or []

        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                columns = tuple(columns)
                for item in table_data:
                    columns = columns if len(columns) > 1 else str(columns).replace(',','')
                    values = ('?,'*len(item)).rstrip(",")
                    query=f"INSERT INTO {self.table_name} {columns} VALUES ({values})"
                    params = item
                    with open("C:/Pruef/issa.txt", 'w', encoding="utf-8") as log:
                        log.write(query + '\n')
                        log.write(str(params) + '\n')
                    cur.execute(query, params)
                conn.commit()
        except IntegrityError:
            pass
        except Error as err:
            print(err)


    def fetch(self, query) -> list:
        """
        Fetches all data from the input query.

        Parameters
            query (str): SQL query

        Returns
            rows (list): Fetched rows list
        """
        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                return rows
        except Error as err:
            print(err)
            return None


    def get_last_row(self) -> tuple:
        """
        Gets the last row of the calling child class.

        Based in the calling child class attributes table_name and primary_key, this
        function will get the last row from the DB table.

        Parameters
            None

        Returns
            last_row (tuple): Fetched last row
        """
        query = f'''
        SELECT *
        FROM {self.table_name}
        ORDER BY {self.primary_key} DESC
        LIMIT 1;
        '''
        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                cur.execute(query)
                return cur.fetchone()
        except Error as err:
            print(err)
            return None


    def is_valid(self, pk_value: str) -> bool:
        """
        Looks if the pk_value exists in the calling child class DB table_name.

        Parameters
            pk_value (str): Primar Key Value to search for it.

        Returns
            is_valid (bool): True if the pk_value exists.
        """
        query = f'''
        SELECT *
        FROM {self.table_name}
        WHERE {self.primary_key} is ?;
        '''
        try:
            with self.create_connection() as conn:
                c = conn.cursor()
                c.execute(query, (pk_value,))
                last_row = c.fetchone()
                if last_row:
                    return True
        except Error as err:
            print(err)
            return False


class ProductTable(ISSA):
    def __init__(self, table_name: str = "Product"):
        super().__init__()
        self.table_name = table_name
        self.primary_key = "serial_number"


    def create(self, create_table_sql: str = "") -> None:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                {self.primary_key} TEXT PRIMARY KEY,
                desc TEXT,
                type TEXT,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        sql = create_table_sql if create_table_sql else sql
        super().create(sql)


    def get_product_dids(self, serial_number: str) -> list:
        """
        Get all test which includes did in their name from the serial number.

        Parameters
            serial_number (str): Device serial number.

        Returns
            rows (list): All results.
        """
        query = f"""
        SELECT 
            t.name AS 'Test Name',
            t.min_limit AS 'Min Limit',
            t.max_limit AS 'Max Limit',
            t.units AS 'Units'
        FROM 
            Test as t
        INNER JOIN
            Product_Test as pt
        ON
            t.id = pt.test_id
        WHERE
            t.name LIKE '%did%' AND pt.serial_number is '{serial_number}';
        """
        rows = self.fetch(query)
        return rows


class BandTable(ISSA):
    def __init__(self, table_name: str = "Band") -> None:
        super().__init__()
        self.table_name = table_name


    def create(self, create_table_sql: str = "") -> None:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                id INTEGER PRIMARY KEY,
                tech TEXT NOT NULL,
                band INTEGER NOT NULL,
                frequency REAL NOT NULL,
                direction TEXT NOT NULL,
                target REAL NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        sql = create_table_sql if create_table_sql else sql
        super().create(sql)
    

    def is_valid(self, tech: str, band: int, freq: float) -> bool:
        query = f"""
            SELECT *
            FROM {self.table_name}
            WHERE tech is '{tech}' AND band is {band} AND frequency is {freq};
        """
        try:
            with self.create_connection() as conn:
                c = conn.cursor()
                c.execute(query)
                last_row = c.fetchone()
                if last_row:
                    return True
        except Error:
            print(Error)
            return False


class ProductBandTable(ISSA):
    def __init__(self, table_name: str = "Product_Band"):
        super().__init__()
        self.table_name = table_name
        self.create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                serial_number TEXT NOT NULL,
                frequency REAL NOT NULL,
                power REAL,
                units TEXT,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(serial_number) REFERENCES ProductTable(serial_number),
                FOREIGN KEY(frequency) REFERENCES BandTable(frequency)
            );
        """


    def create(self) -> None:
        super().create(self.create_table_sql)


    def insert_product_band(self, serial_number: str, tech: str, band: int, frequency: float, power: float, units: str) -> None:
        bt = BandTable()
        if bt.is_valid(tech, band, frequency):
            table_data = {
                "table_name": self.table_name,
                "table_values": [{
                    "serial_number": serial_number,
                    "frequency": frequency,
                    "power": power,
                    "units": units,}]
            }
            self.insert(table_data)
        pass


class LogTable(ISSA):
    def __init__(self, table_name: str = "Log") -> None:
        super().__init__()
        self.table_name = table_name
        self.create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                id INTEGER PRIMARY KEY,
                type TEXT,
                desc TEXT,
                serial_number TEXT,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(serial_number) REFERENCES ProductTable(serial_number)
            );
        """


    def create(self) -> None:
        super().create(self.create_table_sql)


    def get_logs_by_serial_number(self, serial_number: str) -> list:
        query = f'''
        SELECT
            l.serial_number as 'Serial Number',
            l.type as 'Type',
            l.desc as 'Description',
            l.created_on as 'Creation Date'
        FROM Log l 
        WHERE serial_number is '{serial_number}';
        '''
        return self.fetch(query)



class BenchmarkTable(ISSA):
    def __init__(self, table_name: str = "Benchmark") -> None:
        super().__init__()
        self.table_name = table_name


    def create(self, create_table_sql: str = "") -> None:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        sql = create_table_sql if create_table_sql else sql
        super().create(sql)


    def get_id(self, name: str) -> int:
        """
        Get benchmark id from name.

        Parameters
            name    (str): Benchmark name.

        Return
            id      (int): Benchmark id of the requested name.
        """
        query = f"""
            SELECT (id) FROM {self.table_name} WHERE name = '{name}';
        """
        rows = self.fetch(query)
        try:
            return rows[0][0]
        except IndexError:
            pass


class ProductBenchmarkTable(ISSA):
    def __init__(self, table_name: str = "Product_Benchmark"):
        super().__init__()
        self.table_name = table_name
        self.pk_value = ""
        self.create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                id INTEGER PRIMARY KEY,
                serial_number TEXT NOT NULL,
                benchmark_id INTEGER NOT NULL,
                duration_sec INTEGER NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(serial_number) REFERENCES ProductTable(serial_number),
                FOREIGN KEY(benchmark_id) REFERENCES BenchmarkTable(id)
            );
        """


    def create(self) -> None:
        super().create(self.create_table_sql)


    def get_product_benchmark(self, serial_number):
        query = f"""
        SELECT
            pb.serial_number as 'Serial Number',
            b.name as 'Test Step',
            round(pb.duration_sec) as 'Duration in sec',
            pb.created_on as 'Date'
        FROM
            Product_Benchmark pb
        INNER JOIN
            Benchmark b ON b.id = pb.benchmark_id
        WHERE
            pb.serial_number = '{serial_number}';
        """
        try:
            with self.create_connection() as conn:
                c = conn.cursor()
                c.execute(query)
                return c.fetchall()
        except Error as err:
            print(err)


    def insert_product_benchmark(self, serial_number: str, benchmark_name: str, duration_sec: int):
        b = BenchmarkTable()
        benchmark_id = b.get_id(benchmark_name)
        if not benchmark_id:
            table_data = {
                "table_name": "Benchmark",
                "table_values": [{"name": benchmark_name}]
            }
            b.insert(table_data)
            benchmark_id = b.get_id(benchmark_name)
        try:
            with self.create_connection() as conn:
                c = conn.cursor()
                table_data = {
                    "table_name": self.table_name, 
                    "table_values": [{  "serial_number": serial_number, 
                                        "benchmark_id": benchmark_id, 
                                        "duration_sec": duration_sec}]}
                self.insert(table_data)
        except Error as err:
            print(err)


    def get_product_benchmarks(self, serial_numbers: list) -> list:
        return [self.get_product_benchmark(serial_number) for serial_number in serial_numbers]


class TestTable(ISSA):
    """
    Class to represent a Test Table in ISSA.
    """
    def __init__(self, table_name: str = "Test") -> None:
        super().__init__()
        self.table_name = table_name


    def create(self, create_table_sql: str = "") -> None:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                min_limit TEXT NOT NULL,
                max_limit TEXT,
                units TEXT NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        sql = create_table_sql if create_table_sql else sql
        super().create(sql)


    def is_valid(self, name: str) -> bool:
        """
        Verify if table attribute is valid.

        Parameters
            name (str): Table attribute name.

        Returns
            is_valid (bool): If attribute exists, then return True.
        """
        query = f"""
        SELECT id
        FROM { self.table_name }
        WHERE name is '{name}';
        """
        try:
            with self.create_connection() as conn:
                cur = conn.cursor()
                cur.execute(query)
                id = cur.fetchone()
                if id:
                    return True
                else:
                    return False
        except Error as err:
            print(err)


    def get_id(self, name: str) -> int:
        """
        Get test id from name.

        Parameters
            name    (str): Test name.

        Return
            id      (int): Test id of the requested name.
        """
        query = f"""
            SELECT (id) FROM {self.table_name} WHERE name = '{name}';
        """
        rows = self.fetch(query)
        try:
            return rows[0][0]
        except IndexError:
            return None


class ProductTestTable(ISSA):
    def __init__(self, table_name: str = "Product_Test") -> None:
        super().__init__()
        self.table_name = table_name


    def create(self, create_table_sql: str = "") -> None:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                id INTEGER PRIMARY KEY,
                serial_number TEXT NOT NULL,
                test_id INTEGER NOT NULL,
                result TEXT NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(serial_number) REFERENCES ProductTable(serial_number),
                FOREIGN KEY(test_id) REFERENCES BenchmarkTable(id)
            );
        """
        sql = create_table_sql if create_table_sql else sql
        super().create(sql)


    def insert_product_test(self, serial_number: str, tests: list) -> None:
        """
        $Insert a test into a product.

        Parameters
            $serial_number ($str): $Serial Number.

        Returns
            None
        """
        # Log data only for testing purposes
        # with open("../issa/log.txt", 'w') as f:
        #     f.write(serial_number + '\n')
        #     for item in tests:
        #         f.write(str(item) + '\n')

        pt = ProductTestTable()
        test_table = TestTable()
        for test in tests:
            if not test_table.is_valid(test[0]):
                test_table.insert_values(
                    columns=["name", "type", "min_limit", "max_limit", "units"],
                    table_data=[test[:5]]
                )
            test_id = test_table.get_id(test[0])
            print(test_id)
            pt.insert_values(
                columns=["serial_number", "test_id", "result"],
                table_data=[(serial_number, test_id, test[-1])]
            )