from datetime import datetime, timezone, timedelta

# Import Dagster
from dagster import graph, op, OpExecutionContext, In, Nothing, DagsterInstance, RunsFilter

# Import schema, setup and resources
from ..model.schema.location import LocationSpec
from ..model.setup import INITIAL_LOCATIONS
from .common import get_setup_tables_with_resource
from .common import load_location_specs_from_db
from ..resources import PostgresDB

# Import constants
from ..model.setup import KEEP_CHANGESET_DATA_FOR_NUM_DAYS, KEEP_DAGSTER_RUNS_FOR_NUM_DAYS


@op
def maintain_db_integrity(context: OpExecutionContext, postgres_db: PostgresDB) -> Nothing:
    """Check if setup and staging tables were created in target database"""
    
    # Dagster resources exist only in asset/op execution context
    # so we have to link tabsles every run
    setup_tables = get_setup_tables_with_resource(postgres_db)

    # Check DB integrity
    for table in setup_tables.values():
        # Check if table exists and create of necessary
        if not table.exists:
            context.log.info(f"Table \'{table.name}\' is missing in DB")
            # Create table
            table.create(log = context.log)

    # Fill in initial locations if necessary
    coord_table = setup_tables['location_coordinates_tbl']
    for spec in INITIAL_LOCATIONS.values():
        rec_update_required = True
        
        # Read location table from DB
        where_cond = {'location_name': spec.location_name}
        result = coord_table.select(where = [where_cond], log = context.log)
        if result:
            # Result is passed as list of dicts
            # We need only first row assuming location names do not duplicate
            db_spec_record = LocationSpec(result[0])
            # Check initial spec record and db spec record are equal
            if spec == db_spec_record:
                rec_update_required = False
        
        if rec_update_required:
            # If we got here then either row was missing or values were not equal
            # Insert(replace) new record
            context.log.info(f"Update location spec record for location \'{spec.location_name}\' in table \'{coord_table.name}\'")
            val = (spec.location_name, spec.min_lon, spec.min_lat, spec.max_lon, spec.max_lat)
            coord_table.delete(where = [where_cond], log = context.log)
            coord_table.insert(values = [val], log = context.log)
    
    # Load location specs
    location_specs = load_location_specs_from_db(resource = postgres_db, log = context.log)

    # Check statistics integrity
    stats_table = setup_tables['location_load_stats']
    for spec in location_specs:
        where_cond = {'location_name': spec.location_name}
        result = stats_table.select(where = [where_cond], log = context.log)
        if not result:
            # No records for this location, insert new one
            context.log.info(f"Create location spec update statistics record for location \'{spec.location_name}\' in table \'{coord_table.name}\'")
            val = (spec.location_name, None, None, None)
            stats_table.insert(values = [val], log = context.log)
    context.log.info("DB integrity check finished")


@op(ins={"start": In(Nothing)})
def db_housekeeping(context: OpExecutionContext, postgres_db: PostgresDB) -> Nothing:
    """Delete old changeset data"""

    # Dagster resources exist only in asset/op execution context
    # so we have to link tabsles every run
    setup_tables = get_setup_tables_with_resource(postgres_db)

    # Define the time threshold for old data
    time_threshold = datetime.now(timezone.utc) - timedelta(days = KEEP_CHANGESET_DATA_FOR_NUM_DAYS)

    # Delete records from changeset headers table
    table = setup_tables['changeset_headers_tbl']
    table.delete_up_to_ts(fieldname = 'load_timestamp', timestamp = time_threshold, log = context.log)

    # Delete records from changeset data table
    table = setup_tables['changeset_data_tbl']
    table.delete_up_to_ts(fieldname = 'load_timestamp', timestamp = time_threshold, log = context.log)


@op(ins={"start": In(Nothing)})
def dagster_housekeeping(context: OpExecutionContext) -> Nothing:
    """Delete old Dagster run records"""

    instance = DagsterInstance.get()
    # Define the time threshold for old runs
    time_threshold = datetime.now() - timedelta(days = KEEP_DAGSTER_RUNS_FOR_NUM_DAYS)
    # Get old run records
    old_run_records = instance.get_run_records(
        filters = RunsFilter(created_before = time_threshold),
        limit = 10,   # Limit how many are fetched at a time, perform this operation in batches
        ascending = True) # Start from the oldest
    for record in old_run_records:
        # Delete all the database contents for this run
        instance.delete_run(record.dagster_run.run_id)
    context.log.info("DB housekeeping finished")


@graph
def db_maintenance_graph() -> None:
    dagster_housekeeping(start = db_housekeeping(start = maintain_db_integrity()))