from dagster import op, graph, OpExecutionContext
from ..resources import PostgresTargetDB

import psycopg2

from . import CITY_COORDINATES_TBL
from . import CITY_COORDINATES_DATA
from . import CHANGESET_HEADERS_TBL
from . import CHANGESET_DATA_TBL

def _insert_cities_data(context: OpExecutionContext, conn):
	"""Insert base values into CITY_COORDINATES_TBL"""
	
	sql_truncate_str = """
	TRUNCATE TABLE {table_name}
	""".format(table_name = CITY_COORDINATES_TBL)

	sql_insert_str = """
	INSERT INTO {table_name}
		(city, min_lon, min_lat, max_lon, max_lat)
		VALUES %s
	""".format(table_name = CITY_COORDINATES_TBL)

	with conn.cursor() as cursor:
		# Truncate cities table
		cursor.execute(sql_truncate_str)
		conn.commit()

		#Insert values
		psycopg2.extras.execute_values (
			cursor, sql_insert_str, CITY_COORDINATES_DATA, template=None, page_size=100
		)
		conn.commit()


def _create_cities_table(context: OpExecutionContext, conn):					# TODO: Move to resource definition
	"""Create CITY_COORDINATES_TBL"""

	sql_create_str = """
	CREATE TABLE {table_name} (
		city varchar NOT NULL,
		min_lon numeric NOT NULL,
		min_lat numeric NOT NULL,
		max_lon numeric NOT NULL,
		max_lat numeric NOT NULL
	)
	""".format(table_name = CITY_COORDINATES_TBL)

	with conn.cursor() as cursor:
		# Create cities table
		cursor.execute(sql_create_str)
		conn.commit()


@op
def init_target_db(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB):
	"""This op checks if setup and staging tables were created in target database"""
	
	# Check CITY_COORDINATES_TBL
	if not Postgres_Target_DB.table_exists(CITY_COORDINATES_TBL):
		context.log.info("Table \'{table_name}\' is missing".format(
			table_name = CITY_COORDINATES_TBL)
		)
		
		conn = Postgres_Target_DB.connect()	
		try:
			_create_cities_table(context, conn)
			# Check
			if not Postgres_Target_DB.table_exists(CITY_COORDINATES_TBL):
				context.log.error(
					"Table \'{table_name}\' was not created".format(
						table_name = CITY_COORDINATES_TBL)
				)
			else:
				context.log.info(
					"Table \'{table_name}\' was created".format(
						table_name = CITY_COORDINATES_TBL)
				)

			_insert_cities_data(context, conn)
			# Check
			table_lines = Postgres_Target_DB.table_lines(CITY_COORDINATES_TBL)
			if table_lines != len(CITY_COORDINATES_DATA):
				context.log.error(
					"An error occured while populating table \'{table_name}\'".format(
						table_name = CITY_COORDINATES_TBL)
				)
			else:
				context.log.info("Inserted {lines} line(s) into table \'{table_name}\'".format(
						table_name = CITY_COORDINATES_TBL,
						lines = table_lines)
				)
		finally:
			conn.close()

	# Check CHANGESET_HEADERS_TBL
	if not Postgres_Target_DB.table_exists(CITY_COORDINATES_TBL):
		context.log.info("Table \'{table_name}\' is missing".format(
			table_name = CITY_COORDINATES_TBL)
		)


@graph
def init_target_db_graph():
	init_target_db()