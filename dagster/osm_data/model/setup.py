from decimal import Decimal
from typing import Dict

# Import schema
from .schema.location import LocationSpec
from .schema.table import Table

# Import resources
from ..resources import Target_PG_DB


# ============= Setup constants =============

# Number of days to store dagster run records
KEEP_DAGSTER_RUNS_FOR_NUM_DAYS = 7


# ========== Setup tables and data ==========

# Initial locations
INITIAL_LOCATIONS = {
    0:  LocationSpec({
            'location_name': 'St.Petersburg',
            'min_lon': Decimal('30.1245'),
            'min_lat': Decimal('59.8086'),
            'max_lon': Decimal('30.5653'),
            'max_lat': Decimal('60.0926'),
    }),
    1:  LocationSpec({
            'location_name': 'Moscow',
            'min_lon': Decimal('37.3260'),
            'min_lat': Decimal('55.5752'),
            'max_lon': Decimal('37.8754'),
            'max_lat': Decimal('55.9207'),
    }),
    2:  LocationSpec({
            'location_name': 'Yekaterinburg',
            'min_lon': Decimal('60.4866'),
            'min_lat': Decimal('56.7365'),
            'max_lon': Decimal('60.7139'),
            'max_lat': Decimal('56.9191'),
    }),
}

# Setup tables
SETUP_TABLES = {
    'location_coordinates_tbl': Table(
        name = 'osm_location_coordinates',
        column_specs = {
            "location_name":    "varchar UNIQUE NOT NULL",
            "min_lon":          "numeric NOT NULL",
            "min_lat":          "numeric NOT NULL",
            "max_lon":          "numeric NOT NULL",
            "max_lat":          "numeric NOT NULL",
        }
    ),
    'location_load_stats': Table(
        name = 'osm_location_load_stats',
        column_specs = {
            'location_name':                "varchar UNIQUE NOT NULL",
            'update_timestamp':             "timestamp with time zone",
            'initial_load_required':        "boolean",
            'initial_load_start_from_ts':   "timestamp with time zone",
        }
    ),
    'changeset_headers_tbl': Table(
        name = 'osm_changeset_headers',
        column_specs = {
            'load_timestamp':   "timestamp with time zone NOT NULL",
            "location_name":    "varchar NOT NULL",
            'changeset_id':     "bigint NOT NULL",
            'closed_at':        "timestamp with time zone NOT NULL",
            'u_uid':            "bigint NOT NULL",
            'u_username':       "varchar NOT NULL",
            'comment':          "varchar",
            'source':           "varchar",
        }
    ),
    'changeset_data_tbl': Table(
        name = 'osm_changeset_data',
        column_specs = {
            'load_timestamp':   "timestamp with time zone NOT NULL",
            'changeset_id':     "bigint NOT NULL",
            'action':           "varchar NOT NULL",
            'elem_type':        "varchar NOT NULL",
            'elem_id':          "bigint NOT NULL",
            'k':                "varchar",
            'v':                "varchar",
        }
    )
}

def get_setup_tables_with_resource(resource: Target_PG_DB) -> Dict[str, Table]:
    """Dagster resources exist only in asset/op execution context
    so we have to link tabsles every run"""

    setup_tables = SETUP_TABLES
    for table in setup_tables.values():
        table.link_to_resource(resource)
    return(setup_tables)