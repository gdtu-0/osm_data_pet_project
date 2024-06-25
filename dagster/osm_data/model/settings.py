from .schema.table import Table

# ====================== Settings ======================

# DB maintenance interval
RUN_DB_MAINTENANCE_EVERY_NUM_MINUTES = 2

# Number of days to store dagster run records
KEEP_DAGSTER_RUNS_FOR_NUM_DAYS = 7

# Number of days to store changeset data
KEEP_CHANGESET_DATA_FOR_NUM_DAYS = 7

# Number of days to load initial data for location
INITIAL_LOAD_NUM_DAYS = 7

# OSM data update interval
OSM_DATA_UPDATE_INTERVAL_MINUTES = 15

# OSM data pipeline sensor interval
OSM_DPL_SENSOR_UPDATE_INTERVAL_SECONDS = 60


# ==================== Setup tables ====================


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