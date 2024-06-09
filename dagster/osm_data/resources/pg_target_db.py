from dagster import ConfigurableResource

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


	def table_exists(self, table_name: str) -> bool:
		"""Check if table exists in database"""

		sql_str = '''
		SELECT EXISTS (
			SELECT FROM information_schema.tables
				WHERE table_name = \'{table_name}\'
		)
		'''.format(table_name = table_name)

		exists = False
		conn = self.connect()
		try:
			with conn.cursor() as cursor:
				cursor.execute(sql_str)
				exists = cursor.fetchone()[0]
		finally:
			conn.close()
		return(exists)


	def table_lines(self, table_name:str) -> int:
		"""Get number of table lines"""

		sql_str = """
		SELECT COUNT(*) FROM {table_name}
		""".format(table_name = table_name)

		num_lines = 0
		conn = self.connect()
		try:
			with conn.cursor() as cursor:
				cursor.execute(sql_str)
				num_lines = cursor.fetchone()[0]
		finally:
			conn.close()
		return(num_lines)


# --- DEPRECATED ---

	def execute_statement(self, sql_string) -> None:
		"""General method for executing SQL statements"""
		
		conn = self.connect
		try:
			with conn.cursor() as cursor:
				cursor.execute(sql_string)
		finally:
			conn.close()


	def bulk_insert(self, sql_string, data) -> None:
		"""Wrapper for psycopg2.extras.execute_values"""

		conn = self._connect
		try:
			with conn.cursor() as cursor:
				psycopg2.extras.execute_values(cursor, sql_string, data, 
					template=None, page_size=100, fetch=False)
		finally:
			conn.close()