select	uid,
		username
	from {{ ref('stg_osm_changeset_headers') }}
	group by 1, 2