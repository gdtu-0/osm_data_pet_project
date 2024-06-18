from dagster import Definitions

from .assets import ASSET_DEFINITIONS
from .resources import PROJECT_RESOURCES
from .jobs import PROJECT_JOBS
from .jobs import PROJECT_SCHEDULES

# Set dagster definitions
defs = Definitions(
    assets = ASSET_DEFINITIONS,
    resources = PROJECT_RESOURCES,
    jobs = PROJECT_JOBS,
    schedules = PROJECT_SCHEDULES,
)