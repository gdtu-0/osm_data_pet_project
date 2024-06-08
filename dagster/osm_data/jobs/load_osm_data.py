from dagster import define_asset_job

from ..assets import ASSET_DEFINITIONS
from ..ops.db_init import init_target_db_graph

# Define basic asset job
load_osm_data_asset_job = define_asset_job(name='load_osm_data', selection=ASSET_DEFINITIONS)

init_target_db = init_target_db_graph.to_job(name='init_target_db')