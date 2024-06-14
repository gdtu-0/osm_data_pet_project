from dagster import define_asset_job

from ..assets import ASSET_DEFINITIONS
from ..ops.osm_data_pipeline import osm_data_pipeline_graph

# Define basic asset job
load_osm_data_asset_job = define_asset_job(name = 'load_osm_data', selection = ASSET_DEFINITIONS)

#Define op jobs
osm_data_pipeline = osm_data_pipeline_graph.to_job(name = 'osm_data_pipeline')

load_osm_data_jobs = [
	load_osm_data_asset_job,
	osm_data_pipeline
]