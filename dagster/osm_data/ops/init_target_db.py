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
            for val in table['initial_values']:            
                # Read setup table from DB
                where_cond = [f"{list(table['columns'].keys())[0]} = \'{val[0]}\'"] # access row by index field
                res = Postgres_Target_DB.select_from_table(
                            table_name = table['name'],
                            columns = table['columns'],
                            where = where_cond)
                if len(res) > 0:
                    # Result is passed as list of dicts
                    # We take one row and convert it into tuple
                    # as it is represented in setup code
                    res = tuple(res[0].values())
                    # To compare rows we need to stringify values
                    val_stringified = tuple(map(str, val))
                    res_stringified = tuple(map(str, res))
                    if val_stringified == res_stringified:
                        # Values are equal, continue to next row
                        continue
                # If we got here then either row was missing or values were not equal
                # Insert(replace) new record
                Postgres_Target_DB.delete_from_table(
                    table_name = table['name'],
                    where = where_cond)
                Postgres_Target_DB.insert_into_table(
                    table_name = table['name'],
                    columns = table['columns'],
                    values = [val])
                context.log.info(f"Inserted initial record {val} into setup table \'{table['name']}\'")

