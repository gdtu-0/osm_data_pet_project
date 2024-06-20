from dagster import graph, op, OpExecutionContext
from ..resources import PostgresTargetDB

from ..model.setup import INITIAL_LOCATIONS
from . import TABLES_TO_MAINTAIN
from . import LOCATION_COORDINATES_TBL
from . import LOCATION_LOAD_STATS


@op(out = None)
def maintain_db_integrity(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB) -> None:
    """Check if setup and staging tables were created in target database"""
    
    # Check DB integrity
    for table in TABLES_TO_MAINTAIN:
        # Check if table exists and create of necessary
        if not Postgres_Target_DB.table_exists(table['name']):
            context.log.info(f"Table \'{table['name']}\' is missing")
            # Create table
            ddl = Postgres_Target_DB.create_table(
                table_name = table['name'],
                columns = table['column_specs'])
            context.log.info(f"Table \'{table['name']}\' was created with statement:\n\n{ddl}")

    # Fill in initial locations if necessary
    for location_spec in INITIAL_LOCATIONS:
        # Read location table from DB
        where_cond = [f"location_name = \'{location_spec.location_name}\'"]
        res = Postgres_Target_DB.select_from_table(
            table_name = LOCATION_COORDINATES_TBL['name'],
            columns = LOCATION_COORDINATES_TBL['columns'],
            where = where_cond)
        if res:
            # Result is passed as list of dicts
            # We need only first row
            res = res[0]
            rec_mismatch = False
            for key, value in location_spec.to_dict().items():
                if res.get(key, 'NO_KEY') == 'NO_KEY':  # No field in db table
                    continue
                if res.get(key) != value:
                    rec_mismatch = True
                    break
            if rec_mismatch == False:
                # Values are equal, continue to next row
                continue
        # If we got here then either row was missing or values were not equal
        # Insert(replace) new record
        val = (0, location_spec.location_name, location_spec.min_lon, location_spec.min_lat,
               location_spec.max_lon, location_spec.max_lat)
        print(val)
        Postgres_Target_DB.delete_from_table(
            table_name = LOCATION_COORDINATES_TBL['name'],
            where = where_cond)
        Postgres_Target_DB.insert_into_table(
            table_name = LOCATION_COORDINATES_TBL['name'],
            columns = LOCATION_COORDINATES_TBL['columns'],
            values = [val])
        context.log.info(f"Inserted initial record {val} into setup table \'{LOCATION_COORDINATES_TBL['name']}\'")
    
    # Check statistics integrity
    location_specs = Postgres_Target_DB.select_from_table(
        table_name = LOCATION_COORDINATES_TBL['name'],
        columns = LOCATION_COORDINATES_TBL['columns'])
    for location_spec in location_specs:
        where_cond = [f"location_name = \'{location_spec['location_name']}\'"]
        res = Postgres_Target_DB.select_from_table(
            table_name = LOCATION_LOAD_STATS['name'],
            columns = LOCATION_LOAD_STATS['columns'],
            where = where_cond)
        if not res:
            # No records for this location, insert new one
            Postgres_Target_DB.insert_into_table(
                table_name = LOCATION_LOAD_STATS['name'],
                columns = LOCATION_LOAD_STATS['columns'],
                # 'location_name', 'update_timestamp', 'initial_load_required', 'initial_load_start_from_ts'
                values = [(location_spec['location_name'], None, True, None)])
            context.log.info(f"Created statistics record for location \'{location_spec['location_name']}\'")


@graph
def maintain_db_integrity_graph() -> None:
    maintain_db_integrity()