from dagster import ConfigurableResource

import functools
import psycopg2

class PostgresTargetDB(ConfigurableResource):
	"""Dagster resource definition for target Postgres database"""

	dbname: str
	username: str
	password: str
	host: str
	port: int

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
	def table_exists(self, connection, table_name: str) -> bool:
		"""Check if table exists in database"""

		sql_str = '''
		SELECT EXISTS (
			SELECT FROM information_schema.tables
				WHERE table_name = \'{table_name}\'
		)
		'''.format(table_name = table_name)

		exists = False
		with connection.cursor() as cursor:
			cursor.execute(sql_str)
			exists = cursor.fetchone()[0]
		return(exists)		


	@handle_connection
	def table_lines(self, connection, table_name:str) -> int:
		"""Get number of table lines"""

		sql_str = """
		SELECT COUNT(*) FROM {table_name}
		""".format(table_name = table_name)

		num_lines = 0
		with connection.cursor() as cursor:
			cursor.execute(sql_str)
			num_lines = cursor.fetchone()[0]
		return(num_lines)


	@handle_connection
	def create_table(self, connection, table_name:str, columns:list) -> str:
		"""Create table"""

		columns_str = ",\n\t".join(f'{name} {specs}' for name, specs in columns.items())
		sql_str = "CREATE TABLE {table_name} (\n\t{columns_str}\n)".format(
			table_name = table_name,
			columns_str = columns_str)
		with connection.cursor() as cursor:
			cursor.execute(sql_str)
			connection.commit()
		return(sql_str)


	@handle_connection
	def insert_into_table(self, connection, table_name:str, columns:list, values: list):
		"""Insert values into table"""

		columns_str = ", ".join(name for name in columns)
		sql_str = "INSERT INTO {table_name}\n\t({columns_str})\n\t VALUES %s".format(
			table_name = table_name,
			columns_str = columns_str)
		with connection.cursor() as cursor:
			psycopg2.extras.execute_values (
				cursor, sql_str, values, template=None, page_size=100)
			connection.commit()


	@handle_connection
	def truncate_table(self, connection, table_name:str):
		"""Truncate table"""

		sql_str = "TRUNCATE TABLE {table_name}".format(
			table_name = table_name)
		with connection.cursor() as cursor:
			cursor.execute(sql_str)
			connection.commit()