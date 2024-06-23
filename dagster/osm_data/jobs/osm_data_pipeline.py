from dagster import ScheduleDefinition, DefaultScheduleStatus

from ..ops.db_maintenance import db_maintenance_graph
from ..ops.osm_data_pipeline import osm_data_pipeline_manual_run_graph

# DB integrity maintainence job
db_integrity_maintainence_job = db_maintenance_graph.to_job(name = 'db_maintenance')

# DB integrity maintainence schedule
db_integrity_maintainence_schedule = ScheduleDefinition(
    job = db_integrity_maintainence_job,
    cron_schedule = "*/2 * * * *",
    default_status = DefaultScheduleStatus.RUNNING)

# OSM Data pipeline manual job
osm_data_pipeline_manual_run_job = osm_data_pipeline_manual_run_graph.to_job(name = 'osm_data_pipeline_manual_run')

# List of all jobs
osm_data_pipeline_jobs = [
    db_integrity_maintainence_job,
    osm_data_pipeline_manual_run_job,
]

# List of all schedules
osm_data_pipeline_schedules = [
    db_integrity_maintainence_schedule,
]