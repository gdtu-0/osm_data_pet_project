from dagster import ScheduleDefinition, DefaultScheduleStatus

from ..ops.db_integrity import maintain_db_integrity_graph
from ..ops.osm_data_pipeline import osm_data_pipeline_graph

# DB integrity maintainence job
db_integrity_maintainence_job = maintain_db_integrity_graph.to_job(name = 'db_integrity_maintainence')

# DB integrity maintainence schedule
db_integrity_maintainence_schedule = ScheduleDefinition(
    job = db_integrity_maintainence_job,
    cron_schedule = "*/2 * * * *",
    default_status = DefaultScheduleStatus.RUNNING)

# OSM Data pipeline job
osm_data_pipeline_job = osm_data_pipeline_graph.to_job(name = 'osm_data_pipeline')

# OSM Data pipeline schedule
osm_data_pipeline_schedule = ScheduleDefinition(
    job = osm_data_pipeline_job,
    cron_schedule = "*/15 * * * *")

# List of all jobs
osm_data_pipeline_jobs = [
    db_integrity_maintainence_job,
    osm_data_pipeline_job,
]

# List of all schedules
osm_data_pipeline_schedules = [
    db_integrity_maintainence_schedule,
    osm_data_pipeline_schedule,
]