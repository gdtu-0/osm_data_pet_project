with changesets_ordered as (
    select  load_timestamp,
            changeset_id,
            closed_at,
            u_uid,
            comment,
            source,
            location_name,
            row_number() over (
                partition by changeset_id
                order by load_timestamp desc
            ) as changeset_version
    from {{ ref('stg_osm_changeset_headers') }}
),

changeset_stats as (
    select  changeset_id,
            count(distinct elem_id) as create_counter,
            0 as modify_counter,
            0 as delete_counter
        from {{ ref('stg_osm_changeset_data') }}
        where action = 'create'
        group by changeset_id
    union
    select  changeset_id,
            0 as create_countter,
            count(distinct elem_id) as modify_counter,
            0 as delete_counter
        from {{ ref('stg_osm_changeset_data') }}
        where action = 'modify'
        group by changeset_id
    union
    select  changeset_id,
            0 as create_countter,
            0 as modify_counter,
            count(distinct elem_id) as delete_counter
        from {{ ref('stg_osm_changeset_data') }}
        where action = 'delete'
        group by changeset_id
)

select  base.changeset_id,
        base.closed_at,
        base.u_uid,
        base.comment,
        base.source,
        base.location_name,
        sum(stat.create_counter) as create_counter,
        sum(stat.modify_counter) as modify_counter,
        sum(stat.delete_counter) as delete_counter
    from changesets_ordered as base
        inner join changeset_stats as stat
                on stat.changeset_id = base.changeset_id
    where base.changeset_version = 1
    group by    base.changeset_id,
                base.closed_at,
                base.u_uid,
                base.comment,
                base.source,
                base.location_name
    order by 1