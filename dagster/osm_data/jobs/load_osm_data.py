from dagster import define_asset_job

from ..assets import ASSET_DEFINITIONS
from ..ops.init_target_db import init_target_db_graph
from ..ops.osm_data_pipeline import osm_data_pipeline_graph

# Define basic asset job
load_osm_data_asset_job = define_asset_job(name = 'load_osm_data', selection = ASSET_DEFINITIONS)

#Define op jobs
init_target_db = init_target_db_graph.to_job(name = 'init_target_db')
osm_data_pipeline = osm_data_pipeline_graph.to_job(name = 'osm_data_pipeline')

load_osm_data_jobs = [
	load_osm_data_asset_job,
	init_target_db,
	osm_data_pipeline
]