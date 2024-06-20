from dagster import ConfigurableResource

import functools
import psycopg2 # type: ignore
import psycopg2.extras # type: ignore

from typing import Optional, List

class PostgresTargetDB(ConfigurableResource):
    """Dagster resource definition for target Postgres database"""

    dbname:str
    username:str
    password:str
    host:str
    port:int

    def connect(self):
        """Connect to database"""

        return psycopg2.connect(
            dbname = self.dbname,
            user = self.username,
            password = self.password,
            host = self.host,
            port = self.port
        )


    def handle_connection(function):
        """Wrapper for handling connection"""

        @functools.wraps(function)
        def wrapper_handle_connection(self, *args, **kwargs):
            connection = self.connect()
            try:
                value = function(self, connection, *args, **kwargs)
            finally:
                connection.close()
            return(value)
        return wrapper_handle_connection


    @handle_connection
    def table_exists(self, connection, table_name:str) -> bool:
        """Check if table exists in database"""

        sql_str = f"SELECT EXISTS (\n\tSELECT FROM information_schema.tables\n\t\tWHERE table_name = \'{table_name}\'\n)"

        exists = False
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            exists = cursor.fetchone()[0]
        return(exists)      


    @handle_connection
    def table_lines(self, connection, table_name:str) -> int:
        """Get number of table lines"""

        sql_str = f"SELECT COUNT(*) FROM {table_name}"
        num_lines = 0
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            num_lines = cursor.fetchone()[0]
        return(num_lines)


    @handle_connection
    def create_table(self, connection, table_name:str, columns:List[dict]) -> str:
        """Create table"""

        columns_str = ",\n\t".join(f'{name} {specs}' for name, specs in columns.items())
        sql_str = f"CREATE TABLE {table_name} (\n\t{columns_str}\n)"
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            connection.commit()
        return(sql_str)


    @handle_connection
    def insert_into_table(self, connection, table_name:str, columns:tuple, values:List[tuple]):
        """Insert values into table"""

        columns_str = ", ".join(name for name in columns)
        sql_str = f"INSERT INTO {table_name}\n\t({columns_str})\n\t VALUES %s"
        with connection.cursor() as cursor:
            psycopg2.extras.execute_values (
                cursor, sql_str, values, template=None, page_size=100)
            connection.commit()


    @handle_connection
    def truncate_table(self, connection, table_name:str):
        """Truncate table"""

        sql_str = f"TRUNCATE TABLE {table_name}"
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            connection.commit()


    @handle_connection
    def select_from_table(self, connection, table_name:str, columns:tuple, where:Optional[List[str]] = None) -> Optional[list]:          # TODO: A lot to be done here...
        """Select statement (very basic functionality)"""

        columns_str = ",\n\t\t".join(name for name in columns)
        if where is not None:
            where_str = '\tWHERE ' + ",\n\t\tAND ".join(line for line in where)
        else:
            where_str = ''
        sql_str = f"SELECT\t\t{columns_str}\n\tFROM {table_name}\n{where_str}\n;"
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql_str)
            responce = cursor.fetchall()
            if not responce:
                return None
            else:
                result = []
                for row in responce:
                    result.append(dict(row))
                return(result)
    

    @handle_connection
    def delete_from_table(self, connection, table_name:str, where:List[str]):
        """Delete statement"""

        where_str = '\tWHERE ' + ",\n\t\tAND ".join(line for line in where)
        sql_str = f"DELETE FROM {table_name}\n{where_str}\n;"
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql_str)
            connection.commit()
    

    @handle_connection
    def update_table(self, connection, table_name:str, set:List[str], where:List[str]):
        """Update statement"""

        set_str = '\tSET ' + ",\n\t\t".join(line for line in set)
        where_str = '\tWHERE ' + ",\n\t\tAND ".join(line for line in where)
        sql_str = f"UPDATE {table_name}\n{set_str}\n{where_str}\n;"
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql_str)
            connection.commit()