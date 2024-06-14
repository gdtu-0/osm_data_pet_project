from .changeset_data import changeset_data
from .changeset_headers import changeset_headers
from .cities_coordinates import cities_coordinates
from .dbt_assets import osm_data_dbt_assets

# Store asset definitions
ASSET_DEFINITIONS = [changeset_data, changeset_headers, cities_coordinates, osm_data_dbt_assets]