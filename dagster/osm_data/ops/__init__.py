# Table definitions
CITY_COORDINATES_TBL = {
	'name': 'osm_city_coordinates',
	'columns': {
		"city":		"varchar NOT NULL",
		"min_lon":	"numeric NOT NULL",
		"min_lat":	"numeric NOT NULL",
		"max_lon":	"numeric NOT NULL",
		"max_lat":	"numeric NOT NULL"
	},
	# Cities coordinates (insert new cities here)
	'initial_values': [
		('St.Petersburg', 29.65, 59.75, 30.65, 60.10),
	]
}
CHANGESET_HEADERS_TBL = {
	'name': 'osm_changeset_headers',
	'columns': {
		'changeset_id':	"bigint NOT NULL",
		'closed_at':	"timestamp with time zone NOT NULL",
		'username':		"varchar NOT NULL",
		'comment':		"varchar",
		'source':		"varchar"
	}
}
CHANGESET_DATA_TBL = {
	'name': 'osm_changeset_data',
	'columns': {
		'changeset_id':	"bigint NOT NULL",
		'action':		"varchar NOT NULL",
		'elem_type':	"varchar NOT NULL",
		'elem_id':		"bigint NOT NULL",
		'k':			"varchar",
		'v':			"varchar"
	}
}

TABLES_TO_MAINTAIN = [
	CITY_COORDINATES_TBL,
	CHANGESET_HEADERS_TBL,
	CHANGESET_DATA_TBL
]