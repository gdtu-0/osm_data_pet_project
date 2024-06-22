import datetime

# Import Dagster
from dagster import graph, op, OpExecutionContext, In, Nothing, DagsterInstance, RunsFilter

# Import setup
from ..resources import PostgresTargetDB    # TODO: Maybe refactor
from ..model.schema import LocationSpec
from ..model.setup import INITIAL_LOCATIONS
from ..model.setup import SETUP_TABLES

# Import constants
from ..model.setup import KEEP_DAGSTER_RUNS_FOR_NUM_DAYS

@op
def maintain_db_integrity(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB) -> Nothing:
    """Check if setup and staging tables were created in target database"""
    
    # Check DB integrity
    for table in SETUP_TABLES.values():
        # Link tables to resource
        if not table.init_flag:
            table.link_to_resource(Postgres_Target_DB)
        # Check if table exists and create of necessary
        if not table.exists:
            context.log.info(f"Table \'{table.name}\' is missing")
            # Create table
            table.create(log = context.log)

    # Fill in initial locations if necessary
    coord_table = SETUP_TABLES['location_coordinates_tbl']
    for index, location_spec in INITIAL_LOCATIONS.items():
        # Read location table from DB
        where_cond = {'location_name': location_spec.location_name}
        result = coord_table.select(where = where_cond, log = context.log)
        if result:
            # Result is passed as list of dicts
            # We need only first row
            result = result[0]
            rec_mismatch = False
            for key, value in location_spec.to_dict().items():
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
        val = (index, location_spec.location_name, location_spec.min_lon, location_spec.min_lat,
               location_spec.max_lon, location_spec.max_lat)
        coord_table.delete(where = where_cond, log = context.log)
        coord_table.insert(values = [val], log = context.log)
    
    # Load location specs
    location_specs = [LocationSpec(spec) for spec in coord_table.select(log = context.log)]

    # Check statistics integrity
    stats_table = SETUP_TABLES['location_load_stats']
    for location_spec in location_specs:
        where_cond = {'location_name': location_spec.location_name}
        result = stats_table.select(where = where_cond, log = context.log)
        if not result:
            # No records for this location, insert new one
            val = (location_spec.location_name, None, None, None)
            stats_table.insert(values = [val], log = context.log)


@op(ins={"start": In(Nothing)})
def dagster_housekeeping(context: OpExecutionContext) -> Nothing:
    """Delete old Dagster run records"""

    instance = DagsterInstance.get()
    # Define the time threshold for old runs
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=KEEP_DAGSTER_RUNS_FOR_NUM_DAYS)
    # Get old run records
    old_run_records = instance.get_run_records(
        filters=RunsFilter(created_before=time_threshold),
        limit=10,   # Limit how many are fetched at a time, perform this operation in batches
        ascending=True) # Start from the oldest
    for record in old_run_records:
        # Delete all the database contents for this run
        instance.delete_run(record.dagster_run.run_id)


@graph
def db_maintenance_graph() -> None:
    dagster_housekeeping(start = maintain_db_integrity())