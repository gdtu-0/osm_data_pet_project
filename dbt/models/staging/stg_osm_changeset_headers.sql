{{
    config(
        materialized = 'incremental',
        unique_key = 'changeset_id',
        incremental_strategy = 'delete+insert'
    )
}}

select  load_timestamp,
        location_name,
        changeset_id,
        closed_at,
        u_uid,
        u_username,
        comment,
        source
    from {{ source('osm_staging_tables', 'osm_changeset_headers') }}
{% if is_incremental() %}
    where load_timestamp > (select coalesce(max(load_timestamp), TO_TIMESTAMP('2000-01-01 00:00:00','YYYY-MM-DD HH:MI:SS')) from {{ this }})
{% endif %}