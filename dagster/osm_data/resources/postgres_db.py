import functools
import psycopg2 # type: ignore
import psycopg2.extras # type: ignore
from typing import Optional, List, Tuple
from dagster import ConfigurableResource


class PostgresDB(ConfigurableResource):
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

        sql_str = f"SELECT EXISTS (\n\tSELECT FROM information_schema.tables WHERE table_name = \'{table_name}\'\n);"

        exists = False
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            exists = cursor.fetchone()[0]
        return(exists)
    

    @handle_connection
    def exec_sql_dict_cursor(self, connection, sql: str) -> Optional[list]:
        """Execute SQL statement with dict cursor"""

        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql)
            responce = cursor.fetchall()
            if not responce:
                return None
            else:
                result = []
                for row in responce:
                    result.append(dict(row))
                return(result)
    

    @handle_connection
    def exec_sql_no_fetch(self, connection, sql: str) -> None:
        """Execute SQL statement and return nothing"""

        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
    

    @handle_connection
    def exec_insert(self, connection, sql: str, values: List[Tuple]):
        """Special case for insert statement"""

        with connection.cursor() as cursor:
            psycopg2.extras.execute_values (
                cursor, sql, values, template=None, page_size=100)
            connection.commit()