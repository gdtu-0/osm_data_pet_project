with elemelnt_changeset_link as (
    select  elem_id,
            last_changeset_id as changeset_id
        from {{ ref('dds_osm_elements') }}
),
changeset_location_link as (
    select  changeset_id,
            location_name
        from {{ ref('dds_osm_changesets') }}
)

select  e.elem_id as elem_id,
        l.location_name as location_name
    from elemelnt_changeset_link as e
        inner join changeset_location_link as l
                on l.changeset_id = e.changeset_id