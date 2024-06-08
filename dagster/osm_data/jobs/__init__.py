from .load_osm_data import load_osm_data_asset_job
from .load_osm_data import init_target_db

PROJECT_JOBS = [
	load_osm_data_asset_job,
	init_target_db
]