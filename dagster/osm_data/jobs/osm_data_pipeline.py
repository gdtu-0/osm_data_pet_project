from dagster import ScheduleDefinition

from ..ops.osm_data_pipeline import osm_data_pipeline_graph

# OSM Data pipeline job
osm_data_pipeline_job = osm_data_pipeline_graph.to_job(name = 'osm_data_pipeline')

# OSM Data pipeline schedule
osm_data_pipeline_schedule = ScheduleDefinition(
    job = osm_data_pipeline_job,
    cron_schedule = "*/30 * * * *"
)

# List of all jobs
osm_data_pipeline_jobs = [
	osm_data_pipeline_job,
]

# List of all schedules
osm_data_pipeline_schedules = [
    osm_data_pipeline_schedule,
]