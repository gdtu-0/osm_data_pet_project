from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets # type: ignore
from ..resources import DBT_MANIFEST_PATH


# Generate dbt assets
@dbt_assets(manifest = DBT_MANIFEST_PATH)
def osm_data_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context = context).stream()