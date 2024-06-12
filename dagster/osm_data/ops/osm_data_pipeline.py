from dagster import op, graph, OpExecutionContext, Out, DynamicOut, DynamicOutput
from ..resources import PostgresTargetDB, OsmPublicApi

from pandas import DataFrame
from typing import List, Dict, Tuple

from . import CITY_COORDINATES_TBL

@op(out = DynamicOut(Dict))
def get_cities_coordinates(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB) -> DynamicOutput[Dict]:
	"""Read cities coordinates from setup table"""

	# Read setup table from DB
	cities_coordinates = Postgres_Target_DB.select(
		table_name = CITY_COORDINATES_TBL['name'],
		columns = CITY_COORDINATES_TBL['columns'])

	context.log.info("Processing changeset info for citites:\n" + 
		",\n".join(f"{row['index']}: {row['city']}" for row in cities_coordinates))

	# Yield dynamic output
	for row in cities_coordinates:
		yield DynamicOutput(row, mapping_key=f"city_spec_{row['index']}")


@op(out = {"changeset_headers": Out(), "changeset_data": Out()})
def get_changeset_info_for_city(context: OpExecutionContext, OSM_Public_API: OsmPublicApi, city_spec: dict) -> Tuple[DataFrame, DataFrame]:
	"""Get changeset headers and data from API"""

	context.log.info(f"{city_spec['index']}: Thread for {city_spec['city']}\n" + 
						"BBox boundaries are:\n" +
						f"min_lon {city_spec['min_lon']}\tmin_lat {city_spec['min_lat']}\n" +
						f"max_lon {city_spec['max_lon']}\tmax_lat {city_spec['max_lat']}")

	# Get changeset headers
	changeset_headers_df = OSM_Public_API.get_closed_changesets_by_bbox(
		min_lon = city_spec['min_lon'], min_lat = city_spec['min_lat'],
		max_lon = city_spec['max_lon'], max_lat = city_spec['max_lat'])
	changeset_headers_df.insert(0, 'city', city_spec['city'])
	
	# Get changeset data
	changeset_data_df = OSM_Public_API.get_changeset_data(
		changeset_ids = changeset_headers_df['changeset_id'].tolist())

	# Return dataframes
	return(changeset_headers_df, changeset_data_df)


@op
def collect_and_store_results(context: OpExecutionContext, Postgres_Target_DB: PostgresTargetDB, 
		changeset_headers_fan_in: List[DataFrame], changeset_data_fan_in: List[DataFrame]) -> None:
	"""Collect data and save to DB"""

	print(type(changeset_headers_fan_in))
	print(type(changeset_data_fan_in))


@graph
def osm_data_pipeline_graph():
	city_specs = get_cities_coordinates()
	changeset_headers, changeset_data = city_specs.map(get_changeset_info_for_city)
	collect_and_store_results(changeset_headers.collect(), changeset_data.collect())