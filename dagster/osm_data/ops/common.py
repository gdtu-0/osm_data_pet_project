from typing import Optional, List, Dict, Tuple
from datetime import datetime, timezone, timedelta

# Import Dagster
from dagster import DagsterLogManager

# Import schema, setup and resources
from ..model.schema.location import LocationSpec
from ..model.schema.table import Table
from ..model.setup import SETUP_TABLES, INITIAL_LOAD_NUM_DAYS
from ..resources import PostgresDB


def __calculate_load_from_ts() -> datetime:
    """Calculate timestamp for initial load"""
    
    start_from_ts = datetime.now(timezone.utc) - timedelta(days = INITIAL_LOAD_NUM_DAYS)
    start_from_ts = start_from_ts.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    return start_from_ts


def __validate_location_spec_stats(location_spec:LocationSpec) -> None:
    """Validate location spec statistic records"""

    if location_spec.to_dict().get('initial_load_required') is None:
        location_spec.update({'initial_load_required': True})
    
    load_from_ts = location_spec.to_dict().get('initial_load_start_from_ts')
    if location_spec.initial_load_required and load_from_ts is None:
        location_spec.update({'initial_load_start_from_ts': __calculate_load_from_ts()})


def get_setup_tables_with_resource(resource: PostgresDB) -> Dict[str, Table]:
    """Dagster resources exist only in asset/op execution context
    so we have to link tabsles every run"""

    setup_tables = SETUP_TABLES
    for table in setup_tables.values():
        table.link_to_resource(resource)
    return(setup_tables)


def load_location_specs_from_db(resource: PostgresDB, log: Optional[DagsterLogManager] = None) -> List[LocationSpec]:
    """Load location specs from database"""

    # Dagster resources exist only in asset/op execution context
    # so we have to link tabsles every run
    setup_tables = get_setup_tables_with_resource(resource)

    # Location coordinates
    coord_table = setup_tables['location_coordinates_tbl']
    if log:
        log.info("Select location coordinates from DB")
        location_specs = [LocationSpec(row) for row in coord_table.select(log = log)]
    else:
        location_specs = [LocationSpec(row) for row in coord_table.select()]
    
    # Convert to dict structure for easier referencing
    location_specs_dict = {}
    for spec in location_specs:
        location_specs_dict[spec.location_name] = spec
    
    # Location load stats
    stats_table = setup_tables['location_load_stats']
    if log:
        log.info("Select location load stat records from DB")
        load_stats = [LocationSpec(row) for row in stats_table.select(log = log)]
    else:
        load_stats = [LocationSpec(row) for row in stats_table.select()]
    
    # Update location specs
    for stat in load_stats:
        if location_specs_dict.get(stat.location_name):
            location_specs_dict[stat.location_name].update(stat.to_dict())
    
    return list(map(__validate_location_spec_stats, location_specs_dict.values()))


def save_load_stats_to_db(resource: PostgresDB, location_specs: List[LocationSpec], log: Optional[DagsterLogManager] = None) -> None:
    """Save load stats to database"""

    # Dagster resources exist only in asset/op execution context
    # so we have to link tabsles every run
    setup_tables = get_setup_tables_with_resource(resource)

    stats_table = setup_tables['location_load_stats']
    where_cond = list({'location_name': spec.location_name} for spec in location_specs)
    if log:
        log.info("Delete old statistic records and insert new ones")
        stats_table.delete(where = where_cond, log = log)
    else:
        stats_table.delete(where = where_cond)

    # Helper function to construc insert values
    def construct_insert_value(spec: LocationSpec) -> Tuple:
        sd = spec.to_dict()
        out = tuple((
             sd.get('location_name'),
             sd.get('update_timestamp'),
             sd.get('initial_load_required'),
             sd.get('initial_load_start_from_ts'),
        ))
        return out
    
    insert_values = list(map(construct_insert_value, location_specs))
    if log:
        stats_table.insert(values = insert_values, log = log)
    else:
        stats_table.insert(values = insert_values)