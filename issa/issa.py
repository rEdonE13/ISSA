import os
import sqlite3
from sqlite3 import Error, Connection
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
            definition
        fetch():
            Fetches all data from the input query.
        get_last_row():
            Gets the last row of the calling child class.
        is_valid():
            Looks if the pk_value exists in the calling child class DB table_name.
    """
    def __init__(self, db_file: str = "../db/pme.db") -> None:
        self.db_file = db_file
        self.cwd = os.getcwd()
        self.table_name = ""
        self.primary_key = "id"
        self.create_connection()


    def create_connection(self) -> Connection:
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)

    
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
                c = conn.cursor()
                c.executescript(create_table_sql)
        except Error as e:
            print(e)
    
    
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
                c = conn.cursor()
                c.execute(f"DROP TABLE IF EXISTS {self.table_name};")
        except Error as e:
            print(e)


    def insert(self, table_data) -> None:
        """
        Inserts data into the db.

        Parameters
            table_data  (dict): dict containing the table name and values to insert.
        
        Returns
            None
        """
        try:
            with self.create_connection() as conn:
                c = conn.cursor()
                for item in table_data["table_values"]:
                    columns = tuple(item.keys()) if len(item.keys()) > 1 else str(tuple(item.keys())).replace(",", "")
                    values = ('?,'*len(item)).rstrip(",")
                    query=f"INSERT INTO {table_data['table_name']} {columns} VALUES ({values})"
                    params = tuple(item.values())
                    c.execute(query, params)
                conn.commit()
        except IntegrityError as e:
            pass
        except Error as e:
            print(e)


    def insert_values(self, columns: list = [], table_data: list = []) -> None:
        """
        Inserts data from the provided params from TestStand.

        Parameters
            columns     (list): Column names of the DB table.
            table_data  (list): Values for the provided columns.

        Returns
            None
        """
        try:
            with self.create_connection() as conn:
                c = conn.cursor()
                columns = tuple(columns)
                for item in table_data:
                    columns = columns if len(columns) > 1 else str(columns).replace(',','')
                    values = ('?,'*len(item)).rstrip(",")
                    query=f"INSERT INTO {self.table_name} {columns} VALUES ({values})"
                    params = item
                    with open("../issa/log.txt", 'w') as f:
                        f.write(query + '\n')
                        f.write(str(params) + '\n')
                    c.execute(query, params)
                conn.commit()
        except IntegrityError as e:
            pass
        except Error as e:
            print(e)


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
                c = conn.cursor()
                c.execute(query)
                rows = c.fetchall()
                return rows
        except Error as e:
            print(e)
    

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
                c = conn.cursor()
                c.execute(query)
                return c.fetchone()
        except Error as e:
            print(e)


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
        except Error as e:
            print(e)
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


class BandTable(ISSA):
    def __init__(self, table_name: str = "Band") -> None:
        super().__init__()
        self.table_name = table_name
        self.primary_key = "frequency"


    def create(self, create_table_sql: str = "") -> None:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                frequency INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                direction TEXT NOT NULL,
                target REAL NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        sql = create_table_sql if create_table_sql else sql
        super().create(sql)


class ProductBandTable(ISSA):
    def __init__(self, table_name: str = "Product_Band"):
        super().__init__()
        self.table_name = table_name
        self.create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
                serial_number TEXT NOT NULL,
                frequency TEXT NOT NULL,
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
        WHERE  serial_number is '{serial_number}';
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
        except Error as e:
            print(e)


    def get_product_benchmarks(self, serial_numbers: list) -> list:
        return [self.get_product_benchmark(serial_number) for serial_number in serial_numbers]