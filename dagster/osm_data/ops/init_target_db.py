from dagster import op, OpExecutionContext
from ..resources import PostgresTargetDB

from . import TABLES_TO_MAINTAIN
from . import LOCATION_COORDINATES_TBL
from . import LOCATION_LOAD_STATS

@op(out = None)
def init_target_db(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB) -> None:
    """Check if setup and staging tables were created in target database"""
    
    # Check DB consistency
    for table in TABLES_TO_MAINTAIN:
        # Check if table exists and create of necessary
        if not Postgres_Target_DB.table_exists(table['name']):
            context.log.info(f"Table \'{table['name']}\' is missing")
            # Create table
            ddl = Postgres_Target_DB.create_table(
                table_name = table['name'],
                columns = table['column_specs'])
            context.log.info(f"Table \'{table['name']}\' was created with statement:\n\n{ddl}")

        # Fill in default values if any
        if table.get('initial_values', 'NO_KEY') != 'NO_KEY':
            for val in table['initial_values']:            
                # Read setup table from DB
                where_cond = [f"{table['columns'][0]} = \'{val[0]}\'"] # access row by index field
                res = Postgres_Target_DB.select_from_table(
                    table_name = table['name'],
                    columns = table['columns'],
                    where = where_cond)
                if res:
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

    # Check load statistics consistency
    location_specs = Postgres_Target_DB.select_from_table(
        table_name = LOCATION_COORDINATES_TBL['name'],
        columns = LOCATION_COORDINATES_TBL['columns'])
    for location_spec in location_specs:
        where_cond = [f"location_name = {location_spec["location_name"]}"]
        res = Postgres_Target_DB.select_from_table(
            table_name = LOCATION_LOAD_STATS['name'],
            columns = LOCATION_LOAD_STATS['columns'],
            where = [where_cond])
        if not res:
            # No records for this location, insert new one
            Postgres_Target_DB.insert_into_table(
                table_name = LOCATION_LOAD_STATS['name'],
                columns = LOCATION_LOAD_STATS['columns'],
                # 'location_name', 'update_timestamp', 'initial_load_required', 'initial_load_start_from_ts'
                values = [(location_spec["location_name"], None, True, None)])
            context.log.info(f"Created statistics record for location \'{location_spec["location_name"]}\'")