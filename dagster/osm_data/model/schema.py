from dataclasses import dataclass # type: ignore
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

# Schema classes for data model

@dataclass
class LocationSpec:
    """Location specification"""

    location_name: str  # location name
    min_lon: Decimal    # longitude of the left (westernmost) side of the bounding box
    min_lat: Decimal    # latitude of the bottom (southernmost) side of the bounding box
    max_lon: Decimal    # longitude of the right (easternmost) side of the bounding box
    max_lat: Decimal    # latitude of the top (northernmost) side of the bounding box
    update_timestamp: Optional[datetime] = None             # last update timestamp
    initial_load_required: Optional[bool] = None            # initial load flag
    initial_load_start_from_ts: Optional[datetime] = None   # initial load start from

    def to_dict(self) -> Dict:
        """Convert location spec to dict"""
        
        return({
            'location_name': self.location_name,
            'min_lon': self.min_lon,
            'min_lat': self.min_lat,
            'max_lon': self.max_lon,
            'max_lat': self.max_lat,
            'update_timestamp': self.update_timestamp,
            'initial_load_required': self.initial_load_required,
            'initial_load_start_from_ts': self.initial_load_start_from_ts,
        })

@dataclass
class Table:
    """Database table"""

    name: str   # Database table name
    column_specs: Dict  # Dict structure of table fields where key is a field name
                        # and value is column definition
    
    def __post_init__(self) -> None:
        self.columns = tuple(self.column_specs.keys())

# TODO
# class LocationSpecDBInterface:
#     """Class for DB location syncronization"""

#     def __init__(self) -> None:
#         self.dbResource = PROJECT_RESOURCES["Postgres_Target_DB"]

#     def getLocationSpecs(self) -> Optional[List[LocationSpec]]: