with changesets as (
    select  changeset_id,
            closed_at,
            u_uid,
            location_name
        from {{ ref('dds_osm_changesets') }}
),
users as (
    select  u_uid,
            u_username
        from {{ ref('dds_osm_users') }}
),
statistics as (
    select  changeset_id,
            elements_count,
            node_create_count + way_create_count + relation_create_count as create_count,
            node_modify_count + way_modify_count + relation_modify_count as modify_count
        from {{ ref('dds_osm_changeset_statistics') }}
)

select  u.u_uid as uid,
        u.u_username as username,
        date( c.closed_at ) as calday,
        c.location_name as location_name,
        sum( s.elements_count ) as elements_count,
        sum( s.create_count ) as create_count,
        sum( s.modify_count ) as modify_count
    from users as u
        inner join changesets as c
                on c.u_uid = u.u_uid
        inner join statistics as s
                on s.changeset_id = c.changeset_id
    group by 1, 2, 3, 4
