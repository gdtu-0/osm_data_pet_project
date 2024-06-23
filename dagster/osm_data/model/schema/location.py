from pandas import DataFrame # type: ignore
from dataclasses import dataclass # type: ignore
from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal

class LocationSpec:
    """Location specification"""

    # If only i knew about NamedTuple at the moment of writing it...
    # Silly attempt of implementing dict-like structure
    # Stores only keys from __accepted_attrs, type convertion included
    # Attributes are added dynamically and can be accesed like ordinary object attributes

    __accepted_attrs = {
        'location_name': 'str',     # location name
        'min_lon': 'decimal',       # longitude of the left (westernmost) side of the bounding box
        'min_lat': 'decimal',       # latitude of the bottom (southernmost) side of the bounding box
        'max_lon': 'decimal',       # longitude of the right (easternmost) side of the bounding box
        'max_lat': 'decimal',       # latitude of the top (northernmost) side of the bounding box
        'update_timestamp': 'datetime',            # last update timestamp
        'initial_load_required': 'bool',           # initial load flag
        'initial_load_start_from_ts': 'datetime',  # initial load start from
    }

    def __update(self, dict: Dict) -> None:
        """Update self from dict"""

        for name, type in self.__accepted_attrs.items():
            if dict.get(name):
                val = dict[name]
                # Handle serialised records
                if type == 'decimal' and isinstance(val, str):
                    val = Decimal(val)
                elif type == 'datetime' and isinstance(val, str):
                    val = datetime.fromisoformat(val)
                setattr(self, name, val)

    def __init__(self, dict: Dict) -> None:
        """LocationSpec is built from dict"""

        self.__update(dict)
    
    def __eq__(self, other) -> bool:
        """Check LocationSpecs based on attribute values"""

        if type(self) != type(other):
            return False
        for name in self.__accepted_attrs:
            if getattr(self, name, None) != getattr(other, name, None):
                return False
        return True
    
    def __repr__(self) -> str:
        return("LocationSpec: {contents}".format(contents = str(self.to_dict())))
    
    def __str__(self) -> str:
        return("LocationSpec: {contents}".format(contents = str(self.to_dict())))

    def update(self, dict: Dict) -> None:
        """LocationSpec is updated from dict"""

        self.__update(dict)

    def to_dict(self) -> Dict:
        """Convert location spec to dict"""
        
        out = {}
        for name in self.__accepted_attrs.keys():
            val = getattr(self, name, None)
            if val:
                if isinstance(val, Decimal):
                    val = str('{0:f}'.format(val))
                elif isinstance(val, datetime):
                    val = str(val.isoformat())
                out[name] = val
        return out


@dataclass
class LocationData:
    """Structure for transfering location data across pipeline"""

    location_spec: LocationSpec
    changeset_headers: Optional[DataFrame] = None
    changeset_data: Optional[DataFrame] = None