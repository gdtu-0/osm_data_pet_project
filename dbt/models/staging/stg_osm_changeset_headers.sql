with stg_osm_changeset_headers as (
	select *
		from {{ source ('osm_staging_tables', 'osm_changeset_headers') }}
)

select * from stg_osm_changeset_headers