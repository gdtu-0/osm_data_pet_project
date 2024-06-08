from .osm_public_api import OsmPublicApi
from .pg_target_db import PostgresTargetDB

PROJECT_RESOURCES = {
	"OSM_Public_API": OsmPublicApi(),
	"Postgres_target_DB": PostgresTargetDB(),
}