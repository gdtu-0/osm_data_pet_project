select  elem_id,
        v as elem_name
    from {{ ref('dds_osm_element_tags') }}
    where k = 'name'