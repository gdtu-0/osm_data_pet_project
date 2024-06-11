from dagster import op, graph, OpExecutionContext
from ..resources import PostgresTargetDB

from . import TABLES_TO_MAINTAIN

@op
def init_target_db(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB):
	"""This op checks if setup and staging tables were created in target database"""
	
	for table in TABLES_TO_MAINTAIN:
		# Check if table exists and create of necessary
		if not Postgres_Target_DB.table_exists(table['name']):
			context.log.info("Table \'{table_name}\' is missing".format(
				table_name = table['name']))
			# Create table
			ddl = Postgres_Target_DB.create_table(
				table_name = table['name'],
				columns = table['columns'])
			# Check
			if not Postgres_Target_DB.table_exists(table['name']):
				context.log.error("Table \'{table_name}\' was not created".format(
					table_name = table['name']))
				raise Exception("An error occured")
			else:
				context.log.info("Table \'{table_name}\' was created with statement:\n{statement}".format(
					table_name = table['name'],
					statement = ddl))

		# Fill in default values if any
		if table.get('initial_values', 'NO_KEY') != 'NO_KEY':
			if Postgres_Target_DB.table_lines(table['name']) != len(table['initial_values']):
				Postgres_Target_DB.truncate_table(table['name'])
				Postgres_Target_DB.insert_into_table(
					table_name = table['name'],
					columns = table['columns'],
					values = table['initial_values'])

@graph
def init_target_db_graph():
	init_target_db()