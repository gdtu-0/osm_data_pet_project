from dagster import define_asset_job

from ..assets import ASSET_DEFINITIONS

# dbt asset job
run_dbt_modles_job = define_asset_job(name = 'run_dbt_modles', selection = ASSET_DEFINITIONS)

# List of all jobs
run_dbt_modles_jobs = [
	run_dbt_modles_job,
]