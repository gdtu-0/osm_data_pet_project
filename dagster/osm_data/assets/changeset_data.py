from dagster import asset
from pandas import DataFrame

from ..resources import OsmPublicApi

@asset
def changeset_data(changeset_headers: DataFrame, OSM_Public_API: OsmPublicApi) -> DataFrame:
    df_data = []
    for ind in changeset_headers.index:
        df = OSM_Public_API.get_changeset_detailes(changeset_headers['changeset_id'][ind])
        df_data.extend(df.to_dict('records'))
    return DataFrame.from_dict(df_data)