with changesets_ordered as (
    select	load_timestamp,
			changeset_id,
			closed_at,
			uid,
			comment,
			source,
			row_number() over (
				partition by changeset_id
				order by load_timestamp desc
			) as changeset_version
	from {{ ref('stg_osm_changeset_headers') }}    
)

select	changeset_id,
		closed_at,
		uid,
		comment,
		source
	from changesets_ordered
	where changeset_version = 1