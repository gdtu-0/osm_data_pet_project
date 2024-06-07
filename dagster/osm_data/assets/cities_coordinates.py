from dagster import asset, Output, MetadataValue
from pandas import DataFrame

@asset
def cities_coordinates() -> DataFrame:
    coord_l = [
        ['St.Petersburg', 29.65, 59.75, 30.65, 60.10],
    ]
    col_names = [
        'city',
        'min_lon',
        'min_lat',
        'max_lon',
        'max_lat',
    ]
    coord_df = DataFrame(coord_l, columns=col_names)
    return coord_df