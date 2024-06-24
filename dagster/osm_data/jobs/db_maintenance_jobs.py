from dagster import ScheduleDefinition, DefaultScheduleStatus
from ..ops.db_maintenance import db_maintenance_graph
from ..model.settings import RUN_DB_MAINTENANCE_EVERY_NUM_MINUTES

# DB maintainence job
db_maintainence_job = db_maintenance_graph.to_job(name = 'db_maintenance')

# DB maintainence schedule
db_maintainence_schedule = ScheduleDefinition(
    job = db_maintainence_job,
    cron_schedule = f"*/{RUN_DB_MAINTENANCE_EVERY_NUM_MINUTES} * * * *",
    default_status = DefaultScheduleStatus.RUNNING)