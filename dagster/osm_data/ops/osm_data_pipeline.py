from dagster import op, graph, OpExecutionContext, In, Out, DynamicOut, DynamicOutput, Nothing
from ..resources import PostgresTargetDB, OsmPublicApi

from pandas import DataFrame
from typing import List, Dict, Tuple

from datetime import datetime, timezone

from .init_target_db import init_target_db

from . import LOCATION_COORDINATES_TBL
from . import CHANGESET_HEADERS_TBL
from . import CHANGESET_DATA_TBL

@op(ins={"start": In(Nothing)}, out = DynamicOut(Dict))
def get_location_coordinates(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB) -> DynamicOutput[Dict]:
	"""Read location coordinates from setup table"""

	# Read setup table from DB
	location_coordinates = Postgres_Target_DB.select(
		table_name = LOCATION_COORDINATES_TBL['name'],
		columns = LOCATION_COORDINATES_TBL['columns'])

	context.log.info("Processing changeset info for locations:\n" + 
		",\n".join(f"{row['index']}: {row['location_name']}" for row in location_coordinates))

	# Yield dynamic output
	for row in location_coordinates:
		yield DynamicOutput(row, mapping_key=f"location_spec_{row['index']}")


@op(out = {"changeset_headers": Out(), "changeset_data": Out()})
def get_changeset_info_for_location(context: OpExecutionContext, OSM_Public_API: OsmPublicApi, location_spec: dict) -> Tuple[DataFrame, DataFrame]:
	"""Get changeset headers and data from API for location"""

	context.log.info(f"{location_spec['index']}: Thread for location \'{location_spec['location_name']}\'\n" + 
						"BBox boundaries are:\n" +
						f"   min_lon {location_spec['min_lon']}\tmin_lat {location_spec['min_lat']}\n" +
						f"   max_lon {location_spec['max_lon']}\tmax_lat {location_spec['max_lat']}")

	# Get changeset headers
	changeset_headers_df = OSM_Public_API.get_closed_changesets_by_bbox(
		min_lon = location_spec['min_lon'], min_lat = location_spec['min_lat'],
		max_lon = location_spec['max_lon'], max_lat = location_spec['max_lat'])
	changeset_headers_df.insert(0, 'location_name', location_spec['location_name'])
	
	# Get changeset data
	changeset_data_df = OSM_Public_API.get_changeset_data(
		changeset_ids = changeset_headers_df['changeset_id'].tolist())

	# Return dataframes
	return(changeset_headers_df, changeset_data_df)


@op(out = None)
def collect_and_store_results(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB, 
		changeset_headers_fan_in: List[DataFrame], changeset_data_fan_in: List[DataFrame]) -> None:
	"""Collect data and save to DB"""

	load_timestamp = datetime.now(timezone.utc)

	# Save changeset headers
	for df in changeset_headers_fan_in:
		df.insert(0, 'load_timestamp', load_timestamp)
		Postgres_Target_DB.insert_into_table(
			table_name = CHANGESET_HEADERS_TBL['name'],
			columns = df.columns.values.tolist(),
			values = list(df.itertuples(index = False, name = None)))
	context.log.info("Changeset headers saved to DB")

	# Save changeset data
	for df in changeset_data_fan_in:
		df.insert(0, 'load_timestamp', load_timestamp)
		Postgres_Target_DB.insert_into_table(
			table_name = CHANGESET_DATA_TBL['name'],
			columns = df.columns.values.tolist(),
			values = list(df.itertuples(index = False, name = None)))
	context.log.info("Changeset data saved to DB")


@graph
def osm_data_pipeline_graph() -> None:
	location_specs = get_location_coordinates(start = init_target_db())
	changeset_headers, changeset_data = location_specs.map(get_changeset_info_for_location)
	collect_and_store_results(changeset_headers.collect(), changeset_data.collect())