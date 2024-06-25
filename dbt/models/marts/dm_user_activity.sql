select  uid,
        username,
        calday,
        location_name,
        elements_count,
        create_count,
        modify_count
    from {{ ref('dds_osm_user_activity') }}