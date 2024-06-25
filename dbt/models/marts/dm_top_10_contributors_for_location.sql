with activity_ordered as (
    select  uid,
            username,
            calday,
            location_name,
            elements_count,
            row_number() over (
                partition by
                    calday,
                    location_name
                order by
                    elements_count desc
            ) as position
    from {{ ref('dds_osm_user_activity') }}
)

select  calday,
        location_name,
        position,
        uid,
        username,
        elements_count
    from activity_ordered
    where position <= 10
    order by
        calday,
        location_name,
        position
