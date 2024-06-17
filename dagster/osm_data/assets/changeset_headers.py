from dagster import asset
from pandas import DataFrame # type: ignore

from ..resources import OsmPublicApi

@asset
def changeset_headers(cities_coordinates: DataFrame, OSM_Public_API: OsmPublicApi) -> DataFrame:
    df_data = []
    for ind in cities_coordinates.index:
        df = OSM_Public_API.get_closed_changesets_by_bbox(
            min_lon = cities_coordinates['min_lon'][ind],
            min_lat = cities_coordinates['min_lat'][ind],
            max_lon = cities_coordinates['max_lon'][ind],
            max_lat = cities_coordinates['max_lat'][ind],
        )
        df_data.extend(df.to_dict('records'))
    return DataFrame.from_dict(df_data)