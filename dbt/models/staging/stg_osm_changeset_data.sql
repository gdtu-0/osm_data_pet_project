{{
	config(
		materialized = 'incremental',
		unique_key = 'changeset_id',
		incremental_strategy = 'delete+insert'
	)
}}

select	load_timestamp,
		changeset_id,
		action,
		elem_type,
		elem_id,
		k,
		v
	from {{ source('osm_staging_tables', 'osm_changeset_data') }}
{% if is_incremental() %}
	where load_timestamp > (select coalesce(max(load_timestamp), TO_TIMESTAMP('2000-01-01 00:00:00','YYYY-MM-DD HH:MI:SS')) from {{ this }})
{% endif %}