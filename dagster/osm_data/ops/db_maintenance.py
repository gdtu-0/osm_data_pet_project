import datetime

# Import Dagster
from dagster import graph, op, OpExecutionContext, In, Nothing, DagsterInstance, RunsFilter

# Import schema, setup and resources
from ..model.schema import LocationSpec
from ..model.setup import INITIAL_LOCATIONS
from ..model.setup import get_setup_tables_with_resource
from ..resources import Target_PG_DB

# Import constants
from ..model.setup import KEEP_DAGSTER_RUNS_FOR_NUM_DAYS

@op
def maintain_db_integrity(context: OpExecutionContext, Target_PG_DB: Target_PG_DB) -> Nothing:
    """Check if setup and staging tables were created in target database"""
    
    # Dagster resources exist only in asset/op execution context
    # so we have to link tabsles every run
    setup_tables = get_setup_tables_with_resource(Target_PG_DB)

    # Check DB integrity
    for table in setup_tables.values():
        # Check if table exists and create of necessary
        if not table.exists:
            context.log.info(f"Table \'{table.name}\' is missing in DB")
            # Create table
            table.create(log = context.log, logging_enabled = True)

    # Fill in initial locations if necessary
    coord_table = setup_tables['location_coordinates_tbl']
    for index, spec in INITIAL_LOCATIONS.items():
        # Read location table from DB
        where_cond = {'location_name': spec.location_name}
        result = coord_table.select(where = where_cond, log = context.log, logging_enabled = False)
        if result:
            # Result is passed as list of dicts
            # We need only first row
            result = result[0]
            rec_mismatch = False
            for key, value in spec.to_dict().items():
                if result.get(key, 'NO_KEY') == 'NO_KEY':  # No field in db table
                    continue
                if result.get(key) != value:
                    rec_mismatch = True
                    break
            if rec_mismatch == False:
                # Values are equal, continue to next row
                continue
        # If we got here then either row was missing or values were not equal
        # Insert(replace) new record
        context.log.info(f"Update location spec record for location \'{spec.location_name}\' in table \'{coord_table.name}\'")
        val = (index, spec.location_name, spec.min_lon, spec.min_lat,
               spec.max_lon, spec.max_lat)
        coord_table.delete(where = where_cond, log = context.log, logging_enabled = True)
        coord_table.insert(values = [val], log = context.log, logging_enabled = True)
    
    # Load location specs
    context.log.info("Select location spec records from DB")
    location_specs = [LocationSpec(spec) for spec in coord_table.select(log = context.log, logging_enabled = True)]

    # Check statistics integrity
    stats_table = setup_tables['location_load_stats']
    for spec in location_specs:
        where_cond = {'location_name': spec.location_name}
        result = stats_table.select(where = where_cond, log = context.log, logging_enabled = False)
        if not result:
            # No records for this location, insert new one
            context.log.info(f"Create location spec update statistics record for location \'{spec.location_name}\' in table \'{coord_table.name}\'")
            val = (spec.location_name, None, None, None)
            stats_table.insert(values = [val], log = context.log, logging_enabled = True)
    context.log.info("DB integrity check finished")


@op(ins={"start": In(Nothing)})
def dagster_housekeeping(context: OpExecutionContext) -> Nothing:
    """Delete old Dagster run records"""

    instance = DagsterInstance.get()
    # Define the time threshold for old runs
    time_threshold = datetime.datetime.now() - datetime.timedelta(days = KEEP_DAGSTER_RUNS_FOR_NUM_DAYS)
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
    dagster_housekeeping(start = maintain_db_integrity())