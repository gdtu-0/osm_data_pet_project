from pandas import DataFrame # type: ignore
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

# Import Dagster
from dagster import op, graph, OpExecutionContext, In, Out, DynamicOut, DynamicOutput

# Import schema, setup and resources
from ..resources import Target_PG_DB, OsmPublicApi
from ..model.schema.location import LocationSpec, LocationData
from ..model.setup import get_setup_tables_with_resource
from .common import load_location_specs_from_db


@op(out = Out(List[LocationSpec]))
def load_location_specs(context: OpExecutionContext, Target_PG_DB: Target_PG_DB) -> List[LocationSpec]:
    """Read location specs from database"""

    location_specs = load_location_specs_from_db(resource = Target_PG_DB, log = context.log)
    return location_specs


@op(ins = {'location_specs': In(List[LocationSpec])}, out = DynamicOut(LocationSpec))
def schedule_thread_runs(context: OpExecutionContext, location_specs: List[LocationSpec]) -> DynamicOutput[LocationSpec]:
    """For each location spec schedule separate thread run"""
    
    context.log.info("Processing changeset info for locations:\n" + 
        "\n".join(f"{str(index)}: {spec.location_name}" for index, spec in enumerate(location_specs)))

    # Yield dynamic output
    for index, spec in enumerate(location_specs):
        yield DynamicOutput(spec, mapping_key = f"location_spec_{index}")


@op(ins = {'location_spec': In(LocationSpec)}, out = Out(LocationData))
def get_changeset_info_for_location(context: OpExecutionContext, OSM_Public_API: OsmPublicApi, location_spec: LocationSpec) -> LocationData:
    """Get changeset headers and data from API for location"""

    bbox_boundaries_str = ( f"  min_lon: {str(location_spec.min_lon)}\tmin_lat: {str(location_spec.min_lat)}\n" +
                            f"  max_lon: {str(location_spec.max_lon)}\tmax_lat: {str(location_spec.max_lat)}" )
    context.log.info(f"Thread for location \'{location_spec.location_name}\'\nBBox boundaries are:\n{bbox_boundaries_str}")

    # Get changeset headers
    changeset_headers_df = OSM_Public_API.get_closed_changesets_by_bbox(
        min_lon = location_spec.min_lon, min_lat = location_spec.min_lat,
        max_lon = location_spec.max_lon, max_lat = location_spec.max_lat)

    # Add location name
    changeset_headers_df.insert(0, 'location_name', location_spec.location_name)

    # Helper function to clear out irrelevant changesets
    def drop_irrelevant_changeset_headers(location_spec: LocationSpec, changeset_headers: DataFrame) -> DataFrame:
        """Drop changeset with too large areas (they are often scam or service changesets)"""
        
        AREA_DIFF_COEF = Decimal('1.1')    # Maximum area coef diff
        SCALE_FACTOR = Decimal('1000.0')   # Changeset area is too small to calculate prooperly, use scaling factor
        
        spec_bbox_area = (
            (location_spec.max_lat * SCALE_FACTOR - location_spec.min_lat * SCALE_FACTOR) *
            (location_spec.max_lon * SCALE_FACTOR - location_spec.min_lon * SCALE_FACTOR)
        )
        changeset_headers['changeset_area'] = (
            (changeset_headers_df['max_lat'] * SCALE_FACTOR - changeset_headers_df['min_lat'] * SCALE_FACTOR) *
            (changeset_headers_df['max_lon'] * SCALE_FACTOR - changeset_headers_df['min_lon'] * SCALE_FACTOR)
        )

        # Drop irrelevant changesets
        changeset_headers_df.drop(changeset_headers_df[changeset_headers_df['changeset_area'] > spec_bbox_area * AREA_DIFF_COEF].index, inplace = True)
        
        # Drop columns that are not necessary anymore and return
        return(changeset_headers_df.drop(['changeset_area', 'min_lat', 'max_lat', 'min_lon', 'max_lon'], axis = 1))

    # Drop irrelevant changesets
    changeset_headers_df = drop_irrelevant_changeset_headers(
        location_spec = location_spec,
        changeset_headers = changeset_headers_df)

    # Get changeset data
    changeset_data_df = OSM_Public_API.get_changeset_data(
        changeset_ids = changeset_headers_df['changeset_id'].tolist())

    context.log.info(f"Changeset headers line count: {changeset_headers_df.shape[0]}\n" + 
                     f"Changeset data line count: {changeset_data_df.shape[0]}")

    # Pack results to LocationData object
    location_data = LocationData(
        location_spec = location_spec,
        changeset_headers = changeset_headers_df,
        changeset_data = changeset_data_df,
    )

    # Return dataframes
    return location_data


@op(ins = {'location_data_fan_in': In(List[LocationData])}, out = None)
def collect_and_store_results(context: OpExecutionContext, Target_PG_DB: Target_PG_DB, location_data_fan_in: List[LocationData]) -> None:
    """Collect data and save to DB"""

    # Dagster resources exist only in asset/op execution context
    # so we have to link tabsles every run
    setup_tables = get_setup_tables_with_resource(Target_PG_DB)

    # Add load timestamp to data
    load_timestamp = datetime.now(timezone.utc)

    for location_data in location_data_fan_in:
        spec = location_data.location_spec

        # Save changeset headers
        headers_table = setup_tables['changeset_headers_tbl']
        location_data.changeset_headers.insert(0, 'load_timestamp', load_timestamp)
        headers_table.insert(
            values = list(location_data.changeset_headers.itertuples(index = False, name = None)),
            log = context.log, logging_enabled = False)
        context.log.info(f"Changeset headers for location \'{spec.location_name}\' saved to DB.\n" +
                         f"Total records: {location_data.changeset_headers.shape[0]}")

        # Save changeset data
        data_table = setup_tables['changeset_data_tbl']
        location_data.changeset_data.insert(0, 'load_timestamp', load_timestamp)
        data_table.insert(
            values = list(location_data.changeset_data.itertuples(index = False, name = None)),
            log = context.log, logging_enabled = False)
        context.log.info(f"Changeset data for location \'{spec.location_name}\' saved to DB.\n" +
                         f"Total records: {location_data.changeset_data.shape[0]}")


@graph
def osm_data_pipeline_graph() -> None:
    location_specs = schedule_thread_runs(load_location_specs())
    location_data = location_specs.map(get_changeset_info_for_location)
    collect_and_store_results(location_data.collect())