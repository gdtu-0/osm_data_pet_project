from dagster import op, OpExecutionContext
from ..resources import PostgresTargetDB

from . import TABLES_TO_MAINTAIN

@op(out = None)
def init_target_db(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB) -> None:
	"""Check if setup and staging tables were created in target database"""
	
	for table in TABLES_TO_MAINTAIN:
		# Check if table exists and create of necessary
		if not Postgres_Target_DB.table_exists(table['name']):
			context.log.info(f"Table \'{table['name']}\' is missing")
			# Create table
			ddl = Postgres_Target_DB.create_table(
				table_name = table['name'],
				columns = table['columns'])
			# Check
			if not Postgres_Target_DB.table_exists(table['name']):
				context.log.error(f"Table \'{table['name']}\' was not created")
				raise Exception("An error occured")
			else:
				context.log.info(f"Table \'{table['name']}\' was created with statement:\n\n{ddl}")

		# Fill in default values if any
		if table.get('initial_values', 'NO_KEY') != 'NO_KEY':
			if Postgres_Target_DB.table_lines(table['name']) != len(table['initial_values']):
				Postgres_Target_DB.truncate_table(table['name'])
				Postgres_Target_DB.insert_into_table(
					table_name = table['name'],
					columns = table['columns'],
					values = table['initial_values'])
				context.log.info(f"Setup table \'{table['name']}\' initial values updated")
