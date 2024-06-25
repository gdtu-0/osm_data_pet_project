with element_tags as (
    select  stg.elem_id,
            stg.k,
            stg.v
    from {{ ref('stg_osm_changeset_data') }} as stg
        inner join {{ ref('dds_osm_elements') }} as dds
                on stg.elem_id = dds.elem_id
               and stg.changeset_id = dds.last_changeset_id
)

select  elem_id,
        k,
        v
    from element_tags