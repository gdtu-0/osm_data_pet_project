from dagster import op, graph, OpExecutionContext
from ..resources import PostgresTargetDB

import psycopg2

@op
def init_target_db(Postgres_Target_DB: PostgresTargetDB):
	conn = Postgres_Target_DB.connect()
	check_init_tab_exists_sql = '''
		SELECT EXISTS (
			SELECT FROM information_schema.tables
				WHERE table_name = \'osm_cities info\'
		)
	'''
	print(check_init_tab_exists_sql)
	try:
		with conn.cursor() as cursor:
			cursor.execute(check_init_tab_exists_sql)
			responce = cursor.fetchone()
			print(responce[0])
	finally:
		conn.close()

@graph
def init_target_db_graph():
	init_target_db()