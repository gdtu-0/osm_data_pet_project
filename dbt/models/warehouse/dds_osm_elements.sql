with elements_ordered as (
    select  d.load_timestamp,
            d.elem_id,
            d.elem_type,
            d.action,
            d.changeset_id,
            h.location_name,
            row_number() over (
                partition by d.elem_id
                order by d.load_timestamp desc
            ) as elem_version
    from {{ ref('stg_osm_changeset_data') }} as d
        inner join {{ ref('stg_osm_changeset_headers') }} as h
                on h.changeset_id = d.changeset_id
)

select  elem_id,
        elem_type,
        location_name,
        action as last_action,
        changeset_id as last_changeset_id
    from elements_ordered
    where elem_version = 1
    order by 1