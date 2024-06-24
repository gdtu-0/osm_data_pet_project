import os
from pathlib import Path
from dagster import EnvVar
from dagster_dbt import DbtCliResource # type: ignore
from .osm_public_api import OsmPublicApi
from .postgres_db import PostgresDB


DBT_PROJECT_DIR = Path(__file__).joinpath("..", "..", "..", "dbt").resolve()


# List of all project resources
PROJECT_RESOURCES = {
    "osm_public_api": OsmPublicApi(),
    "postgres_db": PostgresDB(
        dbname = EnvVar('TARGET_DB_NAME'),
        username = EnvVar('TARGET_DB_USER'),
        password = EnvVar('TARGET_DB_PASSWORD'),
        host = 'osm_data_db',
        port = 5432),
    "dbt": DbtCliResource(project_dir = os.fspath(DBT_PROJECT_DIR)),
}


# This macro updates dbt manifest file and returns it's path
DBT_MANIFEST_PATH = (
    PROJECT_RESOURCES['dbt'].cli(
        ["--quiet", "parse"],
        target_path = Path("target"),
    )
    .wait()
    .target_path.joinpath("manifest.json")
)