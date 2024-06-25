with element_tags as (
    select  stg.elem_id,
            stg.k,
            stg.v,
            row_number() over (
                partition by stg.elem_id, stg.k
            ) as v_version
    from {{ ref('stg_osm_changeset_data') }} as stg
        inner join {{ ref('dds_osm_elements') }} as dds
                on stg.elem_id = dds.elem_id
               and stg.changeset_id = dds.last_changeset_id
)

select  elem_id,
        k,
        v
    from element_tags
    where v_version = 1