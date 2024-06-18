with elements_ordered as (
    select  load_timestamp,
            elem_id,
            elem_type,
            action,
            row_number() over (
                partition by elem_id
                order by load_timestamp desc
            ) as elem_version
    from {{ ref('stg_osm_changeset_data') }}
)

select  elem_id,
        elem_type,
        action as last_action
    from elements_ordered
    where elem_version = 1