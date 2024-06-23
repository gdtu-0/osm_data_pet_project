from pandas import DataFrame # type: ignore
from dataclasses import dataclass # type: ignore
from typing import Optional, Dict

class LocationSpec:
    """Location specification"""

    # Kinda wrapper for dict that stores only keys from __accepted_names
    # Attributes are added dynamically and can be accesed like ordinary object attributes

    __accepted_attr_names = (
        'location_name',   # location name
        'min_lon',         # longitude of the left (westernmost) side of the bounding box
        'min_lat',         # latitude of the bottom (southernmost) side of the bounding box
        'max_lon',         # longitude of the right (easternmost) side of the bounding box
        'max_lat',         # latitude of the top (northernmost) side of the bounding box
        'update_timestamp',                # last update timestamp
        'initial_load_required',           # initial load flag
        'initial_load_start_from_ts',      # initial load start from
    )

    def __update(self, dict: Dict) -> None:
        """Update self from dict"""

        for name in self.__accepted_attr_names:
            if dict.get(name):
                setattr(self, name, dict[name])

    def __init__(self, dict: Dict) -> None:
        """LocationSpec is built from dict"""

        self.__update(dict)
    
    def __eq__(self, other) -> bool:
        """Check LocationSpecs based on attribute values"""

        if type(self) != type(other):
            return False
        for name in self.__accepted_attr_names:
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
        for name in self.__accepted_attr_names:
            value = getattr(self, name, None)
            if value:
                out[name] = value
        return out


@dataclass
class LocationData:
    """Structure for transfering location data across pipeline"""

    location_spec: LocationSpec
    changeset_headers: Optional[DataFrame] = None
    changeset_data: Optional[DataFrame] = None