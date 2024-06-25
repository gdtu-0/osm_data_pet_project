with elemelnt_location_link as (
    select  elem_id,
            location_name
        from {{ ref('dds_osm_element_location_link') }}
),
element_names as (
    select  elem_id,
            elem_name
        from {{ ref('dds_osm_element_names') }}
),
amenity_elements as (
    select  distinct elem_id
        from {{ ref('dds_osm_element_tags') }}
        where k = 'amenity'
)

select  l.location_name as location_name,
        n.elem_name as amenity_name
    from elemelnt_location_link as l
        inner join element_names as n
                on n.elem_id = l.elem_id
        inner join amenity_elements as a
                on a.elem_id = l.elem_id
    group by 1, 2