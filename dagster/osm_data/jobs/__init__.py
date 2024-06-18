from .osm_data_pipeline import osm_data_pipeline_jobs
from .osm_data_pipeline import osm_data_pipeline_schedules

from .run_dbt_models import run_dbt_modles_jobs

PROJECT_JOBS = [
    *osm_data_pipeline_jobs,
    *run_dbt_modles_jobs,
]

PROJECT_SCHEDULES = [
    *osm_data_pipeline_schedules,
]