from dagster import ScheduleDefinition, DefaultScheduleStatus

from ..ops.db_maintenance import db_maintenance_graph
from ..ops.osm_data_pipeline import osm_data_pipeline_manual_run_graph
from ..ops.osm_data_pipeline import osm_data_pipeline_auto_run_graph

# DB integrity maintainence job
db_integrity_maintainence_job = db_maintenance_graph.to_job(name = 'db_maintenance')

# DB integrity maintainence schedule
db_integrity_maintainence_schedule = ScheduleDefinition(
    job = db_integrity_maintainence_job,
    cron_schedule = "*/2 * * * *",
    default_status = DefaultScheduleStatus.RUNNING)

# OSM Data pipeline manual job
osm_data_pipeline_manual_run_job = osm_data_pipeline_manual_run_graph.to_job(name = 'osm_data_pipeline_manual_run')

# OSM Data pipeline auto job for regular interval runs
osm_data_pipeline_interval_run_job = osm_data_pipeline_auto_run_graph.to_job(name = 'osm_data_pipeline_interval_run')

# OSM Data pipeline auto job for initial load runs
osm_data_pipeline_initial_load_job = osm_data_pipeline_auto_run_graph.to_job(name = 'osm_data_pipeline_initial_load')

# List of all jobs
osm_data_pipeline_jobs = [
    db_integrity_maintainence_job,
    osm_data_pipeline_manual_run_job,
    osm_data_pipeline_interval_run_job,
    osm_data_pipeline_initial_load_job,
]

# List of all schedules
osm_data_pipeline_schedules = [
    db_integrity_maintainence_schedule,
]