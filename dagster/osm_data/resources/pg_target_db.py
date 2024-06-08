from dagster import ConfigurableResource, EnvVar

import psycopg2

class PostgresTargetDB(ConfigurableResource):
	"""Dagster resource definition for target Postgres database"""

	def _connect(self):
		"""Connect to database"""

		return psycopg2.connect(
			dbname = EnvVar('TARGET_DB_NAME'),
			user = EnvVar('TARGET_DB_USER'),
			password = EnvVar('TARGET_DB_PASSWORD'),
			host = 'osm_data_db',
			port = 5432
		)


	def execute_statement(self, sql_string) -> None:
		"""General method for executing SQL statements"""
		conn = self._connect
		cur = conn.cursor()
		cur.execute(sql_string)
		conn.commit()
		cur.close()
		conn.close()

	def bulk_insert(self, sql_string, data) -> None:
		"""Wrapper for psycopg2.extras.execute_values"""

		conn = self._connect
		cur = conn.cursor()
		psycopg2.extras.execute_values(cur, sql_string, data, 
			template=None, page_size=100, fetch=False)
		conn.commit()
		cur.close()
		conn.close()