from ..ops.osm_data_pipeline import (
    osm_data_pipeline_manual_run_graph,
    osm_data_pipeline_auto_run_graph,
)


# OSM Data pipeline manual job
osm_data_pipeline_manual_run_job = osm_data_pipeline_manual_run_graph.to_job(name = 'osm_data_pipeline_manual_run')

# OSM Data pipeline auto job for regular interval runs
osm_data_pipeline_interval_run_job = osm_data_pipeline_auto_run_graph.to_job(name = 'osm_data_pipeline_interval_run')

# OSM Data pipeline auto job for initial load runs
osm_data_pipeline_initial_load_job = osm_data_pipeline_auto_run_graph.to_job(name = 'osm_data_pipeline_initial_load')