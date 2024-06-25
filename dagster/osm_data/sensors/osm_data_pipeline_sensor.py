from datetime import datetime, timezone, timedelta
from ..ops.osm_data_pipeline import PipelineConfig
from ..resources import PostgresDB
from ..model.settings import (
    OSM_DPL_SENSOR_UPDATE_INTERVAL_SECONDS,
    OSM_DATA_UPDATE_INTERVAL_MINUTES
)
from dagster import (
    sensor,
    RunRequest,
    RunConfig,
    SkipReason,
    DefaultSensorStatus,
    RunsFilter,
    DagsterRunStatus,
)
from ..jobs.osm_data_pipeline_jobs import (
    osm_data_pipeline_interval_run_job,
    osm_data_pipeline_initial_load_job,
)
from ..ops.common import (
    load_location_specs_from_db, 
    get_setup_tables_with_resource
)


# List of statses to trigger run
FINISHED_STATUSES = [
    DagsterRunStatus.SUCCESS,
    DagsterRunStatus.FAILURE,
    DagsterRunStatus.CANCELED,
]


def db_init_finnished(resource = PostgresDB) -> bool:
    """Check if all tables were created"""

    tables = get_setup_tables_with_resource(resource = resource)
    for table in tables.values():
        if not table.exists:
            return False
    return True


def can_trigger_run(context, job_name: str) -> bool:
    """Check if previos job execution is finished"""

    run_records = context.instance.get_run_records(filters = RunsFilter(job_name = job_name), order_by = 'create_timestamp', limit = 1)
    if run_records:
        dagster_run = run_records[0].dagster_run
        if not dagster_run.status in FINISHED_STATUSES:
            return False
    return True


def generate_run_request(job_name: str, location_specs: list) -> RunRequest:
    """Generate run request"""

    timestamp_now = datetime.now(timezone.utc)
    return RunRequest(
            run_key = f"{job_name}_{timestamp_now.isoformat(sep = 'T')}",
            job_name = job_name,
            run_config = RunConfig(
                ops={'get_location_specs_from_config': PipelineConfig(location_specs = location_specs)}
                )
            )


@sensor(
        jobs = [osm_data_pipeline_interval_run_job, osm_data_pipeline_initial_load_job],
        default_status = DefaultSensorStatus.RUNNING,
        minimum_interval_seconds = OSM_DPL_SENSOR_UPDATE_INTERVAL_SECONDS,
)
def osm_data_pipeline_sensor(context, postgres_db: PostgresDB):
    """Sensor to trigger pipeline runs"""

    if not db_init_finnished(resource = postgres_db):
        return SkipReason("Database is not consistent")
    else:
        # Load location specs
        location_specs = load_location_specs_from_db(resource = postgres_db)

        # Sort location specs for interval and init load runs
        location_specs_interval_run = []
        location_specs_initial_load = []

        timestamp_now = datetime.now(timezone.utc)
        next_run_offset = timedelta(minutes = OSM_DATA_UPDATE_INTERVAL_MINUTES)
        for spec in location_specs:            
            spec_dict = spec.to_dict()
            if not spec.initial_load_required:
                # Collect specs for interval run
                if spec_dict.get('update_timestamp'):
                    next_run = spec.update_timestamp + next_run_offset
                    if next_run <= timestamp_now:
                        location_specs_interval_run.append(spec_dict)
            else:
                # Collect specs for initial load
                location_specs_initial_load.append(spec_dict)

        # Trigger interval run
        if location_specs_interval_run:
            job_name = 'osm_data_pipeline_interval_run'
            # Check if previous run is finished
            if can_trigger_run(context, job_name):
                context.log.info("f{job_name}:\n\n" + "\n".join(str(elem) for elem in location_specs_interval_run))
                yield generate_run_request(job_name, location_specs_interval_run)
            else:
                context.log.info(f"Skip run. Waiting for job \'{job_name}\' to finish")
                location_specs_interval_run = [] # Reset liist for SkipReason

        # Trigger initial load
        if location_specs_initial_load:
            job_name = 'osm_data_pipeline_initial_load'
            # Check if previous run is finished
            if can_trigger_run(context, job_name):
                context.log.info("f{job_name}:\n\n" + "\n".join(str(elem) for elem in location_specs_initial_load))
                yield generate_run_request(job_name, location_specs_initial_load)
            else:
                context.log.info(f"Skip run. Waiting for job \'{job_name}\' to finish")
                location_specs_initial_load = [] # Reset liist for SkipReason

        
        # If we have nothing to do
        if not location_specs_interval_run and not location_specs_initial_load:
            return SkipReason("Nothing to do")


# List of all sensors
osm_data_pipeline_sensors = [
    osm_data_pipeline_sensor,
]