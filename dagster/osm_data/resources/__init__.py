from dagster import EnvVar

from .osm_public_api import OsmPublicApi
from .pg_target_db import PostgresTargetDB

PROJECT_RESOURCES = {
	"OSM_Public_API": OsmPublicApi(),
	"Postgres_Target_DB": PostgresTargetDB(
		dbname = EnvVar('TARGET_DB_NAME'),
		username = EnvVar('TARGET_DB_USER'),
		password = EnvVar('TARGET_DB_PASSWORD'),
		host = 'osm_data_db',
		port = 5432
	),
}