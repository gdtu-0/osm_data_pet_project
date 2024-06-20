"""
Table definitions

If definition has initial values then the first
field of the table MUST be an index or any field that
acts as a primay key for the table.
"""

LOCATION_COORDINATES_TBL = {
    'name': 'osm_location_coordinates',
    'column_specs': {
        "index":            "integer NOT NULL",
        "location_name":    "varchar NOT NULL",
        "min_lon":          "numeric NOT NULL",
        "min_lat":          "numeric NOT NULL",
        "max_lon":          "numeric NOT NULL",
        "max_lat":          "numeric NOT NULL",
    },
    # Cities coordinates (insert new cities here)
    'initial_values': [
        (0, 'St.Petersburg',    30.1245, 59.8086, 30.5653, 60.0926),
        (1, 'Moscow',           37.3260, 55.5752, 37.8754, 55.9207),
        (2, 'Yekaterinburg',    60.4866, 56.7365, 60.7139, 56.9191),
        # (0, 'FOR_TESTING',      0, 0, 0, 0),
    ],
}

LOCATION_LOAD_STATS = {
    'name': 'osm_location_load_stats',
    'column_specs': {
        'location_name':                "varchar NOT NULL",
        'update_timestamp':             "timestamp with time zone",
        'initial_load_required':        "boolean",
        'initial_load_start_from_ts':   "timestamp with time zone",
    }
}

CHANGESET_HEADERS_TBL = {
    'name': 'osm_changeset_headers',
    'column_specs': {
        'load_timestamp':   "timestamp with time zone NOT NULL",
        "location_name":    "varchar NOT NULL",
        'changeset_id':     "bigint NOT NULL",
        'closed_at':        "timestamp with time zone NOT NULL",
        'u_uid':            "bigint NOT NULL",
        'u_username':       "varchar NOT NULL",
        'comment':          "varchar",
        'source':           "varchar",
    },
}

CHANGESET_DATA_TBL = {
    'name': 'osm_changeset_data',
    'column_specs': {
        'load_timestamp':   "timestamp with time zone NOT NULL",
        'changeset_id':     "bigint NOT NULL",
        'action':           "varchar NOT NULL",
        'elem_type':        "varchar NOT NULL",
        'elem_id':          "bigint NOT NULL",
        'k':                "varchar",
        'v':                "varchar",
    },
}

TABLES_TO_MAINTAIN = [
    LOCATION_COORDINATES_TBL,
    LOCATION_LOAD_STATS,
    CHANGESET_HEADERS_TBL,
    CHANGESET_DATA_TBL,
]

for table in TABLES_TO_MAINTAIN:
    table.update({'columns': tuple(table['column_specs'].keys())})