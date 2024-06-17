# Table definitions
LOCATION_COORDINATES_TBL = {
	'name': 'osm_location_coordinates',
	'columns': {
		"index":			"integer NOT NULL",
		"location_name":	"varchar NOT NULL",
		"min_lon":			"numeric NOT NULL",
		"min_lat":			"numeric NOT NULL",
		"max_lon":			"numeric NOT NULL",
		"max_lat":			"numeric NOT NULL"
	},
	# Cities coordinates (insert new cities here)
	'initial_values': [
		(0, 'St.Petersburg',	29.65, 59.75, 30.65, 60.10),
		(1, 'Moscow',			37.35, 55.56, 37.89, 55.91)
	]
}
CHANGESET_HEADERS_TBL = {
	'name': 'osm_changeset_headers',
	'columns': {
		'load_timestamp':	"timestamp with time zone NOT NULL",
		"location_name":	"varchar NOT NULL",
		'changeset_id':		"bigint NOT NULL",
		'closed_at':		"timestamp with time zone NOT NULL",
        'uid':				"int NOT NULL",
		'username':			"varchar NOT NULL",
		'comment':			"varchar",
		'source':			"varchar"
	}
}
CHANGESET_DATA_TBL = {
	'name': 'osm_changeset_data',
	'columns': {
		'load_timestamp':	"timestamp with time zone NOT NULL",
		'changeset_id':		"bigint NOT NULL",
		'action':			"varchar NOT NULL",
		'elem_type':		"varchar NOT NULL",
		'elem_id':			"bigint NOT NULL",
		'k':				"varchar",
		'v':				"varchar"
	}
}

TABLES_TO_MAINTAIN = [
	LOCATION_COORDINATES_TBL,
	CHANGESET_HEADERS_TBL,
	CHANGESET_DATA_TBL
]