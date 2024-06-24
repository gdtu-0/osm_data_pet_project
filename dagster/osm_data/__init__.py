from dagster import Definitions
from .assets import ASSET_DEFINITIONS
from .resources import PROJECT_RESOURCES
from .jobs import PROJECT_JOBS, PROJECT_SCHEDULES
from .sensors import PROJECT_SENSORS


# Set dagster definitions
defs = Definitions(
    assets = ASSET_DEFINITIONS,
    resources = PROJECT_RESOURCES,
    jobs = PROJECT_JOBS,
    schedules = PROJECT_SCHEDULES,
    sensors = PROJECT_SENSORS,
)