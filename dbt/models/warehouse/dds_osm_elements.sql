with elements_ordered as (
    select  load_timestamp,
            elem_id,
            elem_type,
            action,
            changeset_id,
            row_number() over (
                partition by elem_id
                order by
                    load_timestamp desc,
                    changeset_id desc
            ) as elem_version
    from {{ ref('stg_osm_changeset_data') }}
)

select  elem_id,
        elem_type,
        action as last_action,
        changeset_id as last_changeset_id
    from elements_ordered
    where elem_version = 1