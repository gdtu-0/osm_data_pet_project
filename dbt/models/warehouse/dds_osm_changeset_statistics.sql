with changeset_statistics as (
    select  last_changeset_id as changeset_id,
            count( elem_id ) as node_create_count,
            0 as node_modify_count,
            0 as way_create_count,
            0 as way_modify_count,
            0 as relation_create_count,
            0 as relation_modify_count
        from {{ ref('dds_osm_elements') }}
        where elem_type = 'node'
          and last_action = 'create'
        group by 1
    union
    select  last_changeset_id as changeset_id,
            0 as node_create_count,
            count( elem_id ) as node_modify_count,
            0 as way_create_count,
            0 as way_modify_count,
            0 as relation_create_count,
            0 as relation_modify_count
        from {{ ref('dds_osm_elements') }}
        where elem_type = 'node'
          and last_action = 'modify'
        group by 1
    union
    select  last_changeset_id as changeset_id,
            0 as node_create_count,
            0 as node_modify_count,
            count( elem_id ) as way_create_count,
            0 as way_modify_count,
            0 as relation_create_count,
            0 as relation_modify_count
        from {{ ref('dds_osm_elements') }}
        where elem_type = 'way'
          and last_action = 'create'
        group by 1
    union
    select  last_changeset_id as changeset_id,
            0 as node_create_count,
            0 as node_modify_count,
            0 as way_create_count,
            count( elem_id ) as way_modify_count,
            0 as relation_create_count,
            0 as relation_modify_count
        from {{ ref('dds_osm_elements') }}
        where elem_type = 'way'
          and last_action = 'modify'
        group by 1
    union
    select  last_changeset_id as changeset_id,
            0 as node_create_count,
            0 as node_modify_count,
            0 as way_create_count,
            0 as way_modify_count,
            count( elem_id ) as relation_create_count,
            0 as relation_modify_count
        from {{ ref('dds_osm_elements') }}
        where elem_type = 'relation'
          and last_action = 'create'
        group by 1
    union
    select  last_changeset_id as changeset_id,
            0 as node_create_count,
            0 as node_modify_count,
            0 as way_create_count,
            0 as way_modify_count,
            0 as relation_create_count,
            count( elem_id ) as relation_modify_count
        from {{ ref('dds_osm_elements') }}
        where elem_type = 'relation'
          and last_action = 'modify'
        group by 1
)

select  changeset_id,
        sum( node_create_count + node_modify_count +
             way_create_count + way_modify_count +
             relation_create_count + relation_modify_count
             ) as elements_count,
        sum( node_create_count + node_modify_count
             ) as node_count,
        sum( node_create_count ) as node_create_count,
        sum( node_modify_count ) as node_modify_count,
        sum( way_create_count + way_modify_count
             ) as way_count,
        sum( way_create_count ) as way_create_count,
        sum( way_modify_count ) as way_modify_count,
        sum( relation_create_count + relation_modify_count
             ) as relation_count,
        sum( relation_create_count ) as relation_create_count,
        sum( relation_modify_count ) as relation_modify_count
        from changeset_statistics
        group by 1