from dagster import AssetSelection, Definitions
from dagster import load_assets_from_package_module, define_asset_job
from . import assets
from . import resources

ASSET_GROUP_NAME = 'core_assets'
ASSET_JOB_NAME = 'load_osm_changeset_data'

# Load asset definitions
asset_definitions = load_assets_from_package_module(package_module=assets, group_name='core_assets')

# Define basic asset job
load_osm_changeset_data = define_asset_job(name=ASSET_JOB_NAME, selection=AssetSelection.groups(ASSET_GROUP_NAME))

# Set dagster definitions
defs = Definitions(
    assets=[*asset_definitions],
    jobs=[load_osm_changeset_data],
    resources=resources.PROJECT_RESOURCES
)