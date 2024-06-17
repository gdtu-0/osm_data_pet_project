with stg_osm_changeset_data as (
	select *
		from {{ source ('osm_staging_tables', 'osm_changeset_data') }}
)

select * from stg_osm_changeset_data