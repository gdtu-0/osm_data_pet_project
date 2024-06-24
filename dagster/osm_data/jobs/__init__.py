from .db_maintenance_jobs import (
    db_maintainence_job,
    db_maintainence_schedule,
)
from .osm_data_pipeline_jobs import (
    osm_data_pipeline_manual_run_job,
    osm_data_pipeline_interval_run_job,
    osm_data_pipeline_initial_load_job,
)
from .run_dbt_models import run_dbt_modles_job

PROJECT_JOBS = [
    db_maintainence_job,
    osm_data_pipeline_manual_run_job,
    osm_data_pipeline_interval_run_job,
    osm_data_pipeline_initial_load_job,
    run_dbt_modles_job,
]

PROJECT_SCHEDULES = [
    db_maintainence_schedule,
]